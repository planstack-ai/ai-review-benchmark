package com.example.campaign.service

import com.example.campaign.entity.Campaign
import com.example.campaign.entity.CampaignParticipation
import com.example.campaign.repository.CampaignRepository
import com.example.campaign.repository.CampaignParticipationRepository
import com.example.campaign.exception.CampaignNotFoundException
import com.example.campaign.exception.CampaignNotActiveException
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.List
import java.util.Optional

@Service
@Transactional
class CampaignService {

        private val campaignRepository: CampaignRepository
        private val participationRepository: CampaignParticipationRepository

    @Autowired
    fun CampaignService(campaignRepository: CampaignRepository, 
                          CampaignParticipationRepository participationRepository) {
        campaignRepository = campaignRepository
        participationRepository = participationRepository
    }

    fun Campaign createCampaign(name: String, description: String, startDate: LocalDate, 
                                 LocalDate endDate, BigDecimal budget) {
        Campaign campaign = new Campaign()
        campaign.setName(name)
        campaign.setDescription(description)
        campaign.setStartDate(startDate)
        campaign.setEndDate(endDate)
        campaign.setBudget(budget)
        campaign.setActive(true)
        campaign.setCreatedAt(LocalDateTime.now())
        
        return campaignRepository.save(campaign)
    }

    @Transactional(readOnly = true)
    fun List<Campaign> getActiveCampaigns() {
        LocalDateTime now = LocalDateTime.now()
        return campaignRepository.findAll().stream()
                .filter(this::isCampaignCurrentlyActive)
                .toList()
    }

    fun participateInCampaign(campaignId: Long, userId: String, amount: BigDecimal): CampaignParticipation {
        Campaign campaign = campaignRepository.findById(campaignId)
                .orElseThrow { new CampaignNotFoundException("Campaign not found with id: " + campaignId })

        validateCampaignEligibility(campaign)

        CampaignParticipation participation = new CampaignParticipation()
        participation.setCampaign(campaign)
        participation.setUserId(userId)
        participation.setAmount(amount)
        participation.setParticipatedAt(LocalDateTime.now())

        return participationRepository.save(participation)
    }

    @Transactional(readOnly = true)
    fun calculateTotalParticipation(campaignId: Long): BigDecimal {
        return participationRepository.findByCampaignId(campaignId).stream()
                .map(CampaignParticipation::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
    }

    fun deactivateCampaign(campaignId: Long): {
        Campaign campaign = campaignRepository.findById(campaignId)
                .orElseThrow { new CampaignNotFoundException("Campaign not found with id: " + campaignId })
        
        campaign.setActive(false)
        campaignRepository.save(campaign)
    }

    private fun validateCampaignEligibility(campaign: Campaign): {
        if (!campaign.isActive()) {
            throw new CampaignNotActiveException("Campaign is not active")
        }

        if (!isCampaignCurrentlyActive(campaign)) {
            throw new CampaignNotActiveException("Campaign is not within valid date range")
        }

        BigDecimal totalParticipation = calculateTotalParticipation(campaign.Id)
        if (totalParticipation.compareTo(campaign.Budget) >= 0) {
            throw new CampaignNotActiveException("Campaign budget has been exceeded")
        }
    }

    private fun isCampaignCurrentlyActive(campaign: Campaign): boolean {
        LocalDateTime now = LocalDateTime.now()
        LocalDateTime startDateTime = campaign.StartDate.atStartOfDay()
        
        boolean afterStart = !now.isBefore(startDateTime)
        boolean beforeEnd = now.isBefore(campaign.EndDate.atStartOfDay())
        
        return afterStart && beforeEnd
    }

    @Transactional(readOnly = true)
    fun Optional<Campaign> findCampaignById(campaignId: Long) {
        return campaignRepository.findById(campaignId)
    }

    @Transactional(readOnly = true)
    fun List<CampaignParticipation> getCampaignParticipations(campaignId: Long) {
        return participationRepository.findByCampaignId(campaignId)
    }
}