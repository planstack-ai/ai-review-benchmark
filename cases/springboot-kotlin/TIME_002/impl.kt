package com.example.campaign.service

import com.example.campaign.entity.Campaign
import com.example.campaign.entity.CampaignStatus
import com.example.campaign.repository.CampaignRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.*

@Service
@Transactional
class CampaignService(
    private val campaignRepository: CampaignRepository
) {

    fun findActiveCampaigns(): List<Campaign> {
        return campaignRepository.findAll()
            .filter { isValidCampaign(it) }
            .sortedByDescending { it.priority }
    }

    fun getCampaignById(campaignId: UUID): Campaign? {
        return campaignRepository.findById(campaignId)
            .takeIf { it.isPresent }
            ?.get()
            ?.takeIf { isValidCampaign(it) }
    }

    fun calculateCampaignBudgetUtilization(campaignId: UUID): BigDecimal {
        val campaign = getCampaignById(campaignId) ?: return BigDecimal.ZERO
        
        if (campaign.totalBudget <= BigDecimal.ZERO) {
            return BigDecimal.ZERO
        }

        val utilizationPercentage = campaign.spentBudget
            .divide(campaign.totalBudget, 4, BigDecimal.ROUND_HALF_UP)
            .multiply(BigDecimal.valueOf(100))

        return utilizationPercentage.setScale(2, BigDecimal.ROUND_HALF_UP)
    }

    fun updateCampaignSpending(campaignId: UUID, amount: BigDecimal): Boolean {
        val campaign = getCampaignById(campaignId) ?: return false
        
        if (!isValidCampaign(campaign) || amount <= BigDecimal.ZERO) {
            return false
        }

        val newSpentAmount = campaign.spentBudget.add(amount)
        if (newSpentAmount > campaign.totalBudget) {
            return false
        }

        campaign.spentBudget = newSpentAmount
        campaignRepository.save(campaign)
        return true
    }

    fun deactivateExpiredCampaigns(): Int {
        val allCampaigns = campaignRepository.findAll()
        var deactivatedCount = 0

        allCampaigns.forEach { campaign ->
            if (campaign.status == CampaignStatus.ACTIVE && !isWithinDateRange(campaign)) {
                campaign.status = CampaignStatus.EXPIRED
                campaignRepository.save(campaign)
                deactivatedCount++
            }
        }

        return deactivatedCount
    }

    private fun isValidCampaign(campaign: Campaign): Boolean {
        return campaign.status == CampaignStatus.ACTIVE &&
                isWithinDateRange(campaign) &&
                hasRemainingBudget(campaign)
    }

    private fun isWithinDateRange(campaign: Campaign): Boolean {
        val now = LocalDateTime.now()
        val startValid = !now.isBefore(campaign.startDate.atStartOfDay())
        val endValid = now.isBefore(campaign.endDate.atStartOfDay())
        
        return startValid && endValid
    }

    private fun hasRemainingBudget(campaign: Campaign): Boolean {
        return campaign.spentBudget < campaign.totalBudget
    }

    private fun isEligibleForPromotion(campaign: Campaign): Boolean {
        val utilizationRate = if (campaign.totalBudget > BigDecimal.ZERO) {
            campaign.spentBudget.divide(campaign.totalBudget, 4, BigDecimal.ROUND_HALF_UP)
        } else {
            BigDecimal.ZERO
        }

        return utilizationRate >= BigDecimal.valueOf(0.8) && 
               isWithinDateRange(campaign)
    }
}