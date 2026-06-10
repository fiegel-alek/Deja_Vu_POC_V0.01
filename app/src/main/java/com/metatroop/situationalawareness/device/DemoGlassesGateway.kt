package com.metatroop.situationalawareness.device

import com.metatroop.situationalawareness.vision.CameraFrame
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow

class DemoGlassesGateway : GlassesGateway {
    private val mutableDeviceStatus = MutableStateFlow("Disconnected")
    private val mutableFrames = MutableSharedFlow<CameraFrame>(extraBufferCapacity = 8)

    override val deviceStatus: Flow<String> = mutableDeviceStatus.asStateFlow()
    override val frames: Flow<CameraFrame> = mutableFrames.asSharedFlow()

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
        mutableFrames.tryEmit(
            CameraFrame(
                timestampMs = System.currentTimeMillis(),
                width = 1280,
                height = 720,
                rotationDegrees = 0,
                luminance = 0.42,
                demoSignals = setOf("weapon_visible"),
            ),
        )
    }
}
