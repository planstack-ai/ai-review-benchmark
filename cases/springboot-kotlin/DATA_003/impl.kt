package com.example.ecommerce.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "inventory")
class Inventory(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "product_id", nullable = false, unique = true)
    val productId: Long,

    @Column(nullable = false)
    var quantity: Int = 0,

    @Column(name = "reserved_quantity", nullable = false)
    var reservedQuantity: Int = 0,

    @Column(name = "reorder_level")
    var reorderLevel: Int = 10,

    @Column(name = "last_restocked_at")
    var lastRestockedAt: LocalDateTime? = null,

    @Column(name = "updated_at", nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    val availableQuantity: Int
        get() = quantity - reservedQuantity

    fun needsReorder(): Boolean = availableQuantity <= reorderLevel

    fun decrementQuantity(amount: Int) {
        if (availableQuantity < amount) {
            throw IllegalStateException("Insufficient stock")
        }
        quantity -= amount
    }

    fun incrementQuantity(amount: Int) {
        quantity += amount
        lastRestockedAt = LocalDateTime.now()
    }

    @PreUpdate
    fun preUpdate() {
        updatedAt = LocalDateTime.now()
    }
}
