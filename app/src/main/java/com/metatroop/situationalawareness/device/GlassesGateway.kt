package com.metatroop.situationalawareness.device

import com.metatroop.situationalawareness.alert.Detection
import kotlinx.coroutines.flow.Flow

interface GlassesGateway {
    val deviceStatus: Flow<String>
    val detections: Flow<List<Detection>>

    suspend fun startSession()
    suspend fun stopSession()
    suspend fun speak(message: String)
}
