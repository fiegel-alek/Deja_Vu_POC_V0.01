package com.metatroop.situationalawareness.device

import com.metatroop.situationalawareness.vision.CameraFrame
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow

class DemoGlassesGateway : GlassesGateway {
    private val mutableSessionState = MutableStateFlow(DeviceSessionState.DISCONNECTED)
    private val mutableFrames = MutableSharedFlow<CameraFrame>(extraBufferCapacity = 8)
    private var lastSpokenMessage: String = ""

    override val sessionState: Flow<DeviceSessionState> = mutableSessionState.asStateFlow()
    override val frames: Flow<CameraFrame> = mutableFrames.asSharedFlow()

    override suspend fun startSession() {
        mutableSessionState.value = DeviceSessionState.RUNNING
    }

    override suspend fun stopSession() {
        mutableSessionState.value = DeviceSessionState.STOPPED
    }

    override suspend fun speak(message: String) {
        lastSpokenMessage = message
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

    fun latestSpokenMessage(): String = lastSpokenMessage
}
