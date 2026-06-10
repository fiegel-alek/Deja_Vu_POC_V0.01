package com.metatroop.situationalawareness.device

import com.metatroop.situationalawareness.vision.CameraFrame
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.emptyFlow

class MetaDatGlassesGateway : GlassesGateway {
    private val mutableSessionState = MutableStateFlow(DeviceSessionState.DISCONNECTED)

    override val sessionState: Flow<DeviceSessionState> = mutableSessionState
    override val frames: Flow<CameraFrame> = emptyFlow()

    override suspend fun startSession() {
        mutableSessionState.value = DeviceSessionState.ERROR
    }

    override suspend fun stopSession() {
        mutableSessionState.value = DeviceSessionState.STOPPED
    }

    override suspend fun speak(message: String) {
        mutableSessionState.value = DeviceSessionState.ERROR
    }
}
