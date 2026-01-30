package com.example.ecommerce.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "products")
class Product(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false)
    var name: String,

    var description: String? = null,

    @Column(name = "price_cents", nullable = false)
    var priceCents: Int,

    @Column(nullable = false, unique = true)
    var sku: String,

    @Column(name = "category_id")
    var categoryId: Long? = null,

    @Column(nullable = false)
    var active: Boolean = true,

    @Column(nullable = false)
    var deleted: Boolean = false,

    @Column(name = "deleted_at")
    var deletedAt: LocalDateTime? = null,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at")
    var updatedAt: LocalDateTime? = null
) {
    fun softDelete() {
        deleted = true
        deletedAt = LocalDateTime.now()
        active = false
    }

    fun restore() {
        deleted = false
        deletedAt = null
    }

    val isPurchasable: Boolean
        get() = active && !deleted

    @PreUpdate
    fun preUpdate() {
        updatedAt = LocalDateTime.now()
    }
}
