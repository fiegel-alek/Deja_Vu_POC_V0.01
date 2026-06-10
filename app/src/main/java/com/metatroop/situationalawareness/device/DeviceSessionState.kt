package com.metatroop.situationalawareness.device

enum class DeviceSessionState(val displayText: String) {
    DISCONNECTED("Disconnected"),
    CONNECTING("Connecting"),
    RUNNING("Session running"),
    PAUSED("Session paused"),
    STOPPED("Stopped"),
    ERROR("Device error"),
}
