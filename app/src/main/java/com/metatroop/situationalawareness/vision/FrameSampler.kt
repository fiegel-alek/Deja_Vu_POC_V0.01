package com.metatroop.situationalawareness.vision

class FrameSampler(private val minIntervalMs: Long = DEFAULT_MIN_INTERVAL_MS) {
    private var lastAcceptedTimestampMs: Long? = null

    fun shouldProcess(frame: CameraFrame): Boolean {
        val lastAccepted = lastAcceptedTimestampMs
        if (lastAccepted != null && frame.timestampMs - lastAccepted < minIntervalMs) {
            return false
        }

        lastAcceptedTimestampMs = frame.timestampMs
        return true
    }

    private companion object {
        const val DEFAULT_MIN_INTERVAL_MS = 500L
    }
}
