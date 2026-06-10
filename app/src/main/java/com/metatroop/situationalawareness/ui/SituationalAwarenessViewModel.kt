package com.metatroop.situationalawareness.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.metatroop.situationalawareness.alert.AlertEngine
import com.metatroop.situationalawareness.device.DemoGlassesGateway
import com.metatroop.situationalawareness.device.GlassesGateway
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class SituationalAwarenessUiState(
    val monitoring: Boolean = false,
    val deviceStatus: String = "Disconnected",
    val lastAlertMessage: String = "",
)

class SituationalAwarenessViewModel(
    private val alertEngine: AlertEngine,
    private val glassesGateway: GlassesGateway,
) : ViewModel() {
    private val mutableState = MutableStateFlow(SituationalAwarenessUiState())
    val state: StateFlow<SituationalAwarenessUiState> = mutableState.asStateFlow()

    init {
        viewModelScope.launch {
            glassesGateway.deviceStatus.collectLatest { status ->
                mutableState.update { it.copy(deviceStatus = status) }
            }
        }

        viewModelScope.launch {
            glassesGateway.detections.collectLatest { detections ->
                val alerts = alertEngine.evaluate(detections)
                alerts.firstOrNull()?.let { alert ->
                    glassesGateway.speak(alert.message)
                    mutableState.update { it.copy(lastAlertMessage = alert.message) }
                }
            }
        }
    }

    fun startMonitoring() {
        viewModelScope.launch {
            glassesGateway.startSession()
            mutableState.update { it.copy(monitoring = true) }
        }
    }

    fun stopMonitoring() {
        viewModelScope.launch {
            glassesGateway.stopSession()
            mutableState.update { it.copy(monitoring = false) }
        }
    }

    fun simulateHighConfidenceDetection() {
        (glassesGateway as? DemoGlassesGateway)?.emitDemoDetection()
    }
}

class SituationalAwarenessViewModelFactory(
    private val alertEngine: AlertEngine,
    private val glassesGateway: GlassesGateway,
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return SituationalAwarenessViewModel(alertEngine, glassesGateway) as T
    }
}
