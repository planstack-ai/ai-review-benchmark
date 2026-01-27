package com.example.campaign.service

import com.example.campaign.entity.Campaign
import com.example.campaign.repository.CampaignRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.List
import java.util.Optional

@Service
@Transactional
class CampaignService {

        private val campaignRepository: CampaignRepository
    private final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @Autowired
    fun CampaignService(campaignRepository: CampaignRepository) {
        campaignRepository = campaignRepository
    }

    fun isCampaignActive(campaignId: Long): boolean {
        Optional<Campaign> campaignOpt = campaignRepository.findById(campaignId)
        if (campaignOpt.isEmpty()) {
            return false
        }

        Campaign campaign = campaignOpt.get()
        return isWithinActivePeriod(campaign) && hasValidBudget(campaign)
    }

    fun List<Campaign> getActiveCampaigns() {
        List<Campaign> allCampaigns = campaignRepository.findAll()
        return allCampaigns.stream()
                .filter(this::isWithinActivePeriod)
                .filter(this::hasValidBudget)
                .toList()
    }

    fun calculateRemainingBudget(campaignId: Long): BigDecimal {
        Optional<Campaign> campaignOpt = campaignRepository.findById(campaignId)
        if (campaignOpt.isEmpty()) {
            return BigDecimal.ZERO
        }

        Campaign campaign = campaignOpt.get()
        BigDecimal totalBudget = campaign.TotalBudget
        BigDecimal spentAmount = campaign.SpentAmount
        
        return totalBudget.subtract(spentAmount)
    }

    private fun isWithinActivePeriod(campaign: Campaign): boolean {
        LocalDateTime currentTime = LocalDateTime.now()
        LocalDateTime startTime = campaign.StartDateTime
        LocalDateTime endTime = campaign.EndDateTime

        return currentTime.isAfter(startTime) && currentTime.isBefore(endTime)
    }

    private fun hasValidBudget(campaign: Campaign): boolean {
        BigDecimal remainingBudget = calculateRemainingBudget(campaign.Id)
        return remainingBudget.compareTo(BigDecimal.ZERO) > 0
    }

    fun updateCampaignStatus(campaignId: Long): {
        Optional<Campaign> campaignOpt = campaignRepository.findById(campaignId)
        if (campaignOpt.isEmpty()) {
            return
        }

        Campaign campaign = campaignOpt.get()
        boolean isActive = isCampaignActive(campaignId)
        
        if (isActive && !campaign.isActive()) {
            campaign.setActive(true)
            campaign.setLastUpdated(LocalDateTime.now())
            campaignRepository.save(campaign)
        } else if (!isActive && campaign.isActive()) {
            campaign.setActive(false)
            campaign.setLastUpdated(LocalDateTime.now())
            campaignRepository.save(campaign)
        }
    }

    fun getCampaignStatusReport(campaignId: Long): String {
        Optional<Campaign> campaignOpt = campaignRepository.findById(campaignId)
        if (campaignOpt.isEmpty()) {
            return "Campaign not found"
        }

        Campaign campaign = campaignOpt.get()
        LocalDateTime currentTime = LocalDateTime.now()
        boolean isActive = isCampaignActive(campaignId)
        BigDecimal remainingBudget = calculateRemainingBudget(campaignId)

        return String.format("Campaign %s - Status: %s, Current Time: %s, Remaining Budget: %s",
                campaign.Name,
                isActive ? "ACTIVE" : "INACTIVE",
                currentTime.format(formatter),
                remainingBudget.toString())
    }
}