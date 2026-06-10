package com.metatroop.situationalawareness.device

import com.metatroop.situationalawareness.vision.CameraFrame
import kotlinx.coroutines.flow.Flow

interface GlassesGateway {
    val deviceStatus: Flow<String>
    val frames: Flow<CameraFrame>

    suspend fun startSession()
    suspend fun stopSession()
    suspend fun speak(message: String)
}
