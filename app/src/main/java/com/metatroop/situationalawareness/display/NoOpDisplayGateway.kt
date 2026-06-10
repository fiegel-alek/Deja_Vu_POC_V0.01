package com.metatroop.situationalawareness.display

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class NoOpDisplayGateway : DisplayGateway {
    private val mutableStatus = MutableStateFlow(HudStatus())

    override val status: StateFlow<HudStatus> = mutableStatus.asStateFlow()

    override suspend fun prepare() {
        mutableStatus.value = HudStatus(capability = HudCapability.UNAVAILABLE, enabled = false)
    }

    override suspend fun setEnabled(enabled: Boolean) {
        mutableStatus.value = mutableStatus.value.copy(enabled = false)
    }

    override suspend fun show(card: HudCard) = Unit

    override suspend fun clear() {
        mutableStatus.value = mutableStatus.value.copy(lastCard = null)
    }
}
