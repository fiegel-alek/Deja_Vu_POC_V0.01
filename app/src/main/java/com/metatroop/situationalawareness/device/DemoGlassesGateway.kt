package com.metatroop.situationalawareness.device

import com.metatroop.situationalawareness.alert.Detection
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow

class DemoGlassesGateway : GlassesGateway {
    private val mutableDeviceStatus = MutableStateFlow("Disconnected")
    private val mutableDetections = MutableSharedFlow<List<Detection>>(extraBufferCapacity = 8)

    override val deviceStatus: Flow<String> = mutableDeviceStatus.asStateFlow()
    override val detections: Flow<List<Detection>> = mutableDetections.asSharedFlow()

    override suspend fun startSession() {
        mutableDeviceStatus.value = "Mock device session running"
    }

    override suspend fun stopSession() {
        mutableDeviceStatus.value = "Stopped"
    }

    override suspend fun speak(message: String) {
        mutableDeviceStatus.value = "Spoke: $message"
    }

    fun emitDemoDetection() {
        mutableDetections.tryEmit(
            listOf(
                Detection(
                    label = "weapon_visible",
                    confidence = 0.82,
                    timestampMs = System.currentTimeMillis(),
                    direction = "ahead",
                ),
            ),
        )
    }
}
