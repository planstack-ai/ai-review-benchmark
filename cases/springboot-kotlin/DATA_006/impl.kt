package com.example.ecommerce.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "customers")
class Customer(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false)
    var email: String,

    @Column(name = "first_name")
    var firstName: String? = null,

    @Column(name = "last_name")
    var lastName: String? = null,

    @Column(name = "phone_number")
    var phoneNumber: String? = null,

    var address: String? = null,

    @Column(name = "loyalty_points")
    var loyaltyPoints: Int? = null,

    @Column(name = "loyalty_tier")
    var loyaltyTier: String? = null,

    @Column(name = "total_spent_cents")
    var totalSpentCents: Long? = null,

    @Column(nullable = false)
    var active: Boolean = true,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at")
    var updatedAt: LocalDateTime? = null
) {
    val fullName: String
        get() = "${firstName ?: ""} ${lastName ?: ""}".trim()

    fun getDiscountPercent(): Int {
        val points = loyaltyPoints
        return when {
            points >= 10000 -> 15
            points >= 5000 -> 10
            points >= 1000 -> 5
            else -> 0
        }
    }

    @PreUpdate
    fun preUpdate() {
        updatedAt = LocalDateTime.now()
    }
}
