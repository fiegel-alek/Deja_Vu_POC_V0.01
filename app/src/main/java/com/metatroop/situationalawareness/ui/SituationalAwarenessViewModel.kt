package com.metatroop.situationalawareness.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.metatroop.situationalawareness.alert.AlertLogEntry
import com.metatroop.situationalawareness.alert.AlertLogRepository
import com.metatroop.situationalawareness.device.DemoGlassesGateway
import com.metatroop.situationalawareness.device.DeviceSessionState
import com.metatroop.situationalawareness.device.GlassesGateway
import com.metatroop.situationalawareness.monitoring.FrameProcessor
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class SituationalAwarenessUiState(
    val monitoring: Boolean = false,
    val sessionState: DeviceSessionState = DeviceSessionState.DISCONNECTED,
    val lastAlertMessage: String = "",
    val framesSeen: Int = 0,
    val framesProcessed: Int = 0,
    val detectionsEvaluated: Int = 0,
    val alertsSpoken: Int = 0,
    val alertLog: List<AlertLogEntry> = emptyList(),
)

class SituationalAwarenessViewModel(
    private val glassesGateway: GlassesGateway,
    private val frameProcessor: FrameProcessor,
    private val alertLogRepository: AlertLogRepository,
) : ViewModel() {
    private val mutableState = MutableStateFlow(SituationalAwarenessUiState())
    val state: StateFlow<SituationalAwarenessUiState> = mutableState.asStateFlow()

    init {
        viewModelScope.launch {
            glassesGateway.sessionState.collectLatest { sessionState ->
                mutableState.update { it.copy(sessionState = sessionState) }
            }
        }

        viewModelScope.launch {
            alertLogRepository.entries.collectLatest { alertLog ->
                mutableState.update { it.copy(alertLog = alertLog) }
            }
        }

        viewModelScope.launch {
            glassesGateway.frames.collectLatest { frame ->
                mutableState.update { it.copy(framesSeen = it.framesSeen + 1) }

                val result = frameProcessor.process(frame)
                if (result.processed) {
                    mutableState.update {
                        it.copy(
                            framesProcessed = it.framesProcessed + 1,
                            detectionsEvaluated = it.detectionsEvaluated + result.detectionsEvaluated,
                        )
                    }
                }

                result.alerts.firstOrNull()?.let { alert ->
                    alertLogRepository.record(alert)
                    glassesGateway.speak(alert.message)
                    mutableState.update {
                        it.copy(
                            lastAlertMessage = alert.message,
                            alertsSpoken = it.alertsSpoken + 1,
                        )
                    }
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
    private val glassesGateway: GlassesGateway,
    private val frameProcessor: FrameProcessor,
    private val alertLogRepository: AlertLogRepository,
) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        return SituationalAwarenessViewModel(glassesGateway, frameProcessor, alertLogRepository) as T
    }
}
