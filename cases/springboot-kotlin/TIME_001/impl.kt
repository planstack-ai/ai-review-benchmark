package com.example.campaign.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.*

@Service
@Transactional(readOnly = true)
class CampaignService(
    private val campaignRepository: CampaignRepository,
    private val userRepository: UserRepository
) {

    fun isEligibleForCampaign(userId: Long, campaignId: String): Boolean {
        val campaign = campaignRepository.findByIdAndActiveTrue(campaignId) ?: return false
        val user = userRepository.findById(userId) ?: return false
        
        return isCampaignActive(campaign) && 
               isUserEligible(user, campaign) && 
               !hasUserParticipated(userId, campaignId)
    }

    fun calculateDiscountAmount(originalPrice: BigDecimal, campaignId: String): BigDecimal {
        val campaign = campaignRepository.findByIdAndActiveTrue(campaignId) ?: return BigDecimal.ZERO
        
        if (!isCampaignActive(campaign)) {
            return BigDecimal.ZERO
        }
        
        return when (campaign.discountType) {
            DiscountType.PERCENTAGE -> originalPrice.multiply(campaign.discountValue).divide(BigDecimal(100))
            DiscountType.FIXED_AMOUNT -> campaign.discountValue.min(originalPrice)
            else -> BigDecimal.ZERO
        }
    }

    @Transactional
    fun participateInCampaign(userId: Long, campaignId: String): CampaignParticipationResult {
        if (!isEligibleForCampaign(userId, campaignId)) {
            return CampaignParticipationResult.INELIGIBLE
        }
        
        val campaign = campaignRepository.findByIdAndActiveTrue(campaignId)!!
        val currentParticipants = campaignRepository.countParticipants(campaignId)
        
        if (currentParticipants >= campaign.maxParticipants) {
            return CampaignParticipationResult.CAPACITY_EXCEEDED
        }
        
        campaignRepository.addParticipant(userId, campaignId, getCurrentJapanTime())
        return CampaignParticipationResult.SUCCESS
    }

    private fun isCampaignActive(campaign: Campaign): Boolean {
        val now = getCurrentJapanTime()
        return now.isAfter(campaign.startTime) && now.isBefore(campaign.endTime)
    }

    private fun isUserEligible(user: User, campaign: Campaign): Boolean {
        return user.membershipLevel >= campaign.requiredMembershipLevel &&
               user.totalPurchaseAmount >= campaign.minimumPurchaseAmount
    }

    private fun hasUserParticipated(userId: Long, campaignId: String): Boolean {
        return campaignRepository.findParticipation(userId, campaignId) != null
    }

    private fun getCurrentJapanTime(): LocalDateTime {
        return LocalDateTime.now()
    }

    fun getActiveCampaigns(): List<CampaignSummary> {
        val allCampaigns = campaignRepository.findAllByActiveTrue()
        val currentTime = getCurrentJapanTime()
        
        return allCampaigns
            .filter { it.startTime.isBefore(currentTime) && it.endTime.isAfter(currentTime) }
            .map { campaign ->
                CampaignSummary(
                    id = campaign.id,
                    name = campaign.name,
                    description = campaign.description,
                    discountValue = campaign.discountValue,
                    discountType = campaign.discountType,
                    endTime = campaign.endTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")),
                    remainingSlots = campaign.maxParticipants - campaignRepository.countParticipants(campaign.id)
                )
            }
            .sortedBy { it.endTime }
    }
}

data class CampaignSummary(
    val id: String,
    val name: String,
    val description: String,
    val discountValue: BigDecimal,
    val discountType: DiscountType,
    val endTime: String,
    val remainingSlots: Int
)

enum class CampaignParticipationResult {
    SUCCESS, INELIGIBLE, CAPACITY_EXCEEDED
}

enum class DiscountType {
    PERCENTAGE, FIXED_AMOUNT
}