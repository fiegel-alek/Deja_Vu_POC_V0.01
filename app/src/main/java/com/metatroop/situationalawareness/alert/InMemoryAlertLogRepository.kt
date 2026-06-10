package com.metatroop.situationalawareness.alert

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class InMemoryAlertLogRepository(private val maxEntries: Int = 100) : AlertLogRepository {
    private val mutableEntries = MutableStateFlow<List<AlertLogEntry>>(emptyList())

    override val entries: StateFlow<List<AlertLogEntry>> = mutableEntries.asStateFlow()

    override fun record(alert: Alert) {
        mutableEntries.value = listOf(alert.toLogEntry()) + mutableEntries.value.take(maxEntries - 1)
    }

    private fun Alert.toLogEntry(): AlertLogEntry {
        return AlertLogEntry(
            label = label,
            confidence = confidence,
            timestampMs = timestampMs,
            message = message,
            severity = severity,
        )
    }
}
