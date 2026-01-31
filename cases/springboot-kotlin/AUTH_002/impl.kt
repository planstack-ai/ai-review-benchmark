package com.example.ecommerce.service

import com.example.ecommerce.entity.Cart
import com.example.ecommerce.entity.CartItem
import com.example.ecommerce.entity.Product
import com.example.ecommerce.entity.User
import com.example.ecommerce.repository.CartRepository
import com.example.ecommerce.repository.CartItemRepository
import com.example.ecommerce.repository.ProductRepository
import com.example.ecommerce.dto.CartItemRequest
import com.example.ecommerce.dto.CartResponse
import com.example.ecommerce.exception.CartNotFoundException
import com.example.ecommerce.exception.ProductNotFoundException
import com.example.ecommerce.exception.InsufficientStockException
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime

@Service
@Transactional
class CartService(
    private val cartRepository: CartRepository,
    private val cartItemRepository: CartItemRepository,
    private val productRepository: ProductRepository
) {

    fun addItemToCart(cartId: Long, request: CartItemRequest, currentUser: User): CartResponse {
        val cart = findCartById(cartId)
        val product = findProductById(request.productId)
        
        validateStockAvailability(product, request.quantity)
        
        val existingItem = cart.items.find { it.product.id == request.productId }
        
        if (existingItem != null) {
            updateExistingCartItem(existingItem, request.quantity)
        } else {
            createNewCartItem(cart, product, request.quantity)
        }
        
        updateCartTotals(cart)
        val savedCart = cartRepository.save(cart)
        
        return mapToCartResponse(savedCart)
    }

    fun updateCartItemQuantity(cartId: Long, itemId: Long, quantity: Int, currentUser: User): CartResponse {
        val cart = findCartById(cartId)
        val cartItem = cart.items.find { it.id == itemId }
            ?: throw CartNotFoundException("Cart item not found")
        
        if (quantity <= 0) {
            removeCartItem(cart, cartItem)
        } else {
            validateStockAvailability(cartItem.product, quantity)
            cartItem.quantity = quantity
            cartItem.subtotal = cartItem.product.price.multiply(BigDecimal(quantity))
            cartItem.updatedAt = LocalDateTime.now()
        }
        
        updateCartTotals(cart)
        val savedCart = cartRepository.save(cart)
        
        return mapToCartResponse(savedCart)
    }

    fun removeItemFromCart(cartId: Long, itemId: Long, currentUser: User): CartResponse {
        val cart = findCartById(cartId)
        val cartItem = cart.items.find { it.id == itemId }
            ?: throw CartNotFoundException("Cart item not found")
        
        removeCartItem(cart, cartItem)
        updateCartTotals(cart)
        val savedCart = cartRepository.save(cart)
        
        return mapToCartResponse(savedCart)
    }

    fun clearCart(cartId: Long, currentUser: User): CartResponse {
        val cart = findCartById(cartId)
        
        cartItemRepository.deleteAll(cart.items)
        cart.items.clear()
        cart.totalAmount = BigDecimal.ZERO
        cart.itemCount = 0
        cart.updatedAt = LocalDateTime.now()
        
        val savedCart = cartRepository.save(cart)
        return mapToCartResponse(savedCart)
    }

    private fun findCartById(cartId: Long): Cart {
        return cartRepository.findById(cartId)
            .orElseThrow { CartNotFoundException("Cart not found with id: $cartId") }
    }

    private fun findProductById(productId: Long): Product {
        return productRepository.findById(productId)
            .orElseThrow { ProductNotFoundException("Product not found with id: $productId") }
    }

    private fun validateStockAvailability(product: Product, requestedQuantity: Int) {
        if (product.stockQuantity < requestedQuantity) {
            throw InsufficientStockException("Insufficient stock for product: ${product.name}")
        }
    }

    private fun updateExistingCartItem(cartItem: CartItem, additionalQuantity: Int) {
        cartItem.quantity += additionalQuantity
        cartItem.subtotal = cartItem.product.price.multiply(BigDecimal(cartItem.quantity))
        cartItem.updatedAt = LocalDateTime.now()
    }

    private fun createNewCartItem(cart: Cart, product: Product, quantity: Int) {
        val cartItem = CartItem(
            cart = cart,
            product = product,
            quantity = quantity,
            unitPrice = product.price,
            subtotal = product.price.multiply(BigDecimal(quantity))
        )
        cart.items.add(cartItem)
    }

    private fun removeCartItem(cart: Cart, cartItem: CartItem) {
        cart.items.remove(cartItem)
        cartItemRepository.delete(cartItem)
    }

    private fun updateCartTotals(cart: Cart) {
        cart.totalAmount = cart.items.sumOf { it.subtotal }
        cart.itemCount = cart.items.sumOf { it.quantity }
        cart.updatedAt = LocalDateTime.now()
    }

    private fun mapToCartResponse(cart: Cart): CartResponse {
        return CartResponse(
            id = cart.id!!,
            userId = cart.user.id!!,
            items = cart.items.map { item ->
                CartResponse.CartItemResponse(
                    id = item.id!!,
                    productId = item.product.id!!,
                    productName = item.product.name,
                    quantity = item.quantity,
                    unitPrice = item.unitPrice,
                    subtotal = item.subtotal
                )
            },
            totalAmount = cart.totalAmount,
            itemCount = cart.itemCount,
            updatedAt = cart.updatedAt
        )
    }
}