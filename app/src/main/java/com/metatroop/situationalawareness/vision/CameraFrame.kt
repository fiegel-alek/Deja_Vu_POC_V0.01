package com.metatroop.situationalawareness.vision

data class CameraFrame(
    val timestampMs: Long,
    val width: Int,
    val height: Int,
    val rotationDegrees: Int,
    val luminance: Double? = null,
    val demoSignals: Set<String> = emptySet(),
)
