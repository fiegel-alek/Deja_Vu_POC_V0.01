package com.metatroop.situationalawareness.monitoring

import com.metatroop.situationalawareness.alert.Alert

data class FrameProcessingResult(
    val processed: Boolean,
    val detectionsEvaluated: Int = 0,
    val alerts: List<Alert> = emptyList(),
)
