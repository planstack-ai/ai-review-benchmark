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

    @Column(nullable = false)
    var active: Boolean = true,

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "category_id")
    var category: Category? = null,

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "supplier_id")
    var supplier: Supplier? = null,

    @OneToMany(mappedBy = "product", fetch = FetchType.EAGER, cascade = [CascadeType.ALL])
    val reviews: MutableList<Review> = mutableListOf(),

    @OneToOne(mappedBy = "product", fetch = FetchType.EAGER, cascade = [CascadeType.ALL])
    var inventory: Inventory? = null,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at")
    var updatedAt: LocalDateTime? = null
) {
    fun getAverageRating(): Double {
        if (reviews.isEmpty()) return 0.0
        return reviews.map { it.rating }.average()
    }

    fun isInStock(): Boolean {
        return inventory?.let { it.availableQuantity > 0 } ?: false
    }

    @PreUpdate
    fun preUpdate() {
        updatedAt = LocalDateTime.now()
    }
}

@Entity
@Table(name = "categories")
class Category(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    var name: String,

    var description: String? = null,

    @OneToMany(mappedBy = "category")
    val products: MutableList<Product> = mutableListOf()
)

@Entity
@Table(name = "reviews")
class Review(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    val product: Product,

    val rating: Int,

    val comment: String? = null,

    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "inventory")
class Inventory(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    val product: Product,

    var quantity: Int = 0,

    var reservedQuantity: Int = 0
) {
    val availableQuantity: Int
        get() = quantity - reservedQuantity
}

@Entity
@Table(name = "suppliers")
class Supplier(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    var name: String,

    var contactEmail: String,

    var phone: String? = null
)
