package com.metatroop.situationalawareness.alert

import kotlinx.coroutines.flow.StateFlow

data class AlertLogEntry(
    val label: String,
    val confidence: Double,
    val timestampMs: Long,
    val message: String,
    val severity: Int,
)

interface AlertLogRepository {
    val entries: StateFlow<List<AlertLogEntry>>

    fun record(alert: Alert)
}
