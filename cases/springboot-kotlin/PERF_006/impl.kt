package com.example.ecommerce.service

import com.example.ecommerce.entity.User
import com.example.ecommerce.repository.UserRepository
import org.springframework.cache.annotation.CacheEvict
import org.springframework.cache.annotation.Cacheable
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class UserProfileService(
    private val userRepository: UserRepository
) {
    @Cacheable("userProfile")
    @Transactional(readOnly = true)
    fun getUserProfile(userId: Long): Map<String, Any?>? {
        val user = userRepository.findById(userId).orElse(null) ?: return null

        return mapOf(
            "id" to user.id,
            "email" to user.email,
            "firstName" to user.firstName,
            "lastName" to user.lastName,
            "phone" to user.phone,
            "address" to user.address
        )
    }

    @Cacheable("userProfile")
    @Transactional(readOnly = true)
    fun getUser(userId: Long): User? {
        return userRepository.findById(userId).orElse(null)
    }

    @CacheEvict(value = ["userProfile"], allEntries = true)
    @Transactional
    fun updateUserProfile(userId: Long, updates: Map<String, String>): User {
        val user = userRepository.findById(userId)
            .orElseThrow { IllegalArgumentException("User not found: $userId") }

        updates["firstName"]?.let { user.firstName = it }
        updates["lastName"]?.let { user.lastName = it }
        updates["phone"]?.let { user.phone = it }
        updates["address"]?.let { user.address = it }

        return userRepository.save(user)
    }

    @Cacheable("userProfile")
    @Transactional(readOnly = true)
    fun getUserPreferences(userId: Long): Map<String, Any> {
        val user = userRepository.findById(userId).orElse(null)
            ?: return emptyMap()

        return mapOf(
            "userId" to user.id,
            "notificationsEnabled" to true,
            "theme" to "light",
            "language" to "en"
        )
    }
}
