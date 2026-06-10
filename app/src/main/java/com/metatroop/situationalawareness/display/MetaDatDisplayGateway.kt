package com.metatroop.situationalawareness.display

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class MetaDatDisplayGateway : DisplayGateway {
    private val mutableStatus = MutableStateFlow(HudStatus())

    override val status: StateFlow<HudStatus> = mutableStatus.asStateFlow()

    override suspend fun prepare() {
        mutableStatus.value = HudStatus(capability = HudCapability.PREPARING, enabled = false)
        mutableStatus.value =
            HudStatus(
                capability = HudCapability.ERROR,
                enabled = false,
            )
    }

    override suspend fun setEnabled(enabled: Boolean) {
        mutableStatus.value = mutableStatus.value.copy(enabled = enabled && mutableStatus.value.capability == HudCapability.READY)
    }

    override suspend fun show(card: HudCard) {
        val current = mutableStatus.value
        if (current.capability == HudCapability.READY && current.enabled) {
            mutableStatus.value = current.copy(lastCard = card)
        }
    }

    override suspend fun clear() {
        mutableStatus.value = mutableStatus.value.copy(lastCard = null)
    }
}
