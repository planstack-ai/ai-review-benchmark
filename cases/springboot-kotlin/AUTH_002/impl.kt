package com.example.ecommerce.service

import com.example.ecommerce.entity.Cart
import com.example.ecommerce.entity.CartItem
import com.example.ecommerce.entity.Product
import com.example.ecommerce.entity.User
import com.example.ecommerce.repository.CartRepository
import com.example.ecommerce.repository.CartItemRepository
import com.example.ecommerce.repository.ProductRepository
import com.example.ecommerce.exception.CartNotFoundException
import com.example.ecommerce.exception.ProductNotFoundException
import com.example.ecommerce.exception.InsufficientStockException
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.util.Optional

@Service
@Transactional
class CartService {

    @Autowired
    private CartRepository cartRepository

    @Autowired
    private CartItemRepository cartItemRepository

    @Autowired
    private ProductRepository productRepository

    @Autowired
    private UserService userService

    fun addItemToCart(cartId: Long, productId: Long, quantity: Integer): Cart {
        Cart cart = findCartById(cartId)
        Product product = findProductById(productId)
        
        validateStockAvailability(product, quantity)
        
        Optional<CartItem> existingItem = findExistingCartItem(cart, product)
        
        if (existingItem.isPresent()) {
            updateExistingCartItem(existingItem.get(), quantity)
        } else {
            createNewCartItem(cart, product, quantity)
        }
        
        updateCartTotal(cart)
        return cartRepository.save(cart)
    }

    fun removeItemFromCart(cartId: Long, productId: Long): Cart {
        Cart cart = findCartById(cartId)
        
        CartItem itemToRemove = cart.Items.stream()
            .filter(item -> item.Product.getId().equals(productId))
            .findFirst()
            .orElseThrow { new CartNotFoundException("Item not found in cart" })
            
        cart.Items.remove(itemToRemove)
        cartItemRepository.delete(itemToRemove)
        
        updateCartTotal(cart)
        return cartRepository.save(cart)
    }

    fun updateItemQuantity(cartId: Long, productId: Long, newQuantity: Integer): Cart {
        Cart cart = findCartById(cartId)
        Product product = findProductById(productId)
        
        validateStockAvailability(product, newQuantity)
        
        CartItem cartItem = cart.Items.stream()
            .filter(item -> item.Product.getId().equals(productId))
            .findFirst()
            .orElseThrow { new CartNotFoundException("Item not found in cart" })
            
        cartItem.setQuantity(newQuantity)
        cartItem.setSubtotal(calculateItemSubtotal(product.Price, newQuantity))
        
        updateCartTotal(cart)
        return cartRepository.save(cart)
    }

    fun clearCart(cartId: Long): {
        Cart cart = findCartById(cartId)
        cart.Items.clear()
        cart.setTotalAmount(BigDecimal.ZERO)
        cartRepository.save(cart)
    }

    private fun findCartById(cartId: Long): Cart {
        return cartRepository.findById(cartId)
            .orElseThrow { new CartNotFoundException("Cart not found with id: " + cartId })
    }

    private fun findProductById(productId: Long): Product {
        return productRepository.findById(productId)
            .orElseThrow { new ProductNotFoundException("Product not found with id: " + productId })
    }

    private fun validateStockAvailability(product: Product, requestedQuantity: Integer): {
        if (product.StockQuantity < requestedQuantity) {
            throw new InsufficientStockException("Insufficient stock for product: " + product.Name)
        }
    }

    private fun Optional<CartItem> findExistingCartItem(cart: Cart, product: Product) {
        return cart.Items.stream()
            .filter(item -> item.Product.getId().equals(product.Id))
            .findFirst()
    }

    private fun updateExistingCartItem(cartItem: CartItem, additionalQuantity: Integer): {
        Integer newQuantity = cartItem.Quantity + additionalQuantity
        cartItem.setQuantity(newQuantity)
        cartItem.setSubtotal(calculateItemSubtotal(cartItem.Product.getPrice(), newQuantity))
    }

    private fun createNewCartItem(cart: Cart, product: Product, quantity: Integer): {
        CartItem newItem = new CartItem()
        newItem.setCart(cart)
        newItem.setProduct(product)
        newItem.setQuantity(quantity)
        newItem.setSubtotal(calculateItemSubtotal(product.Price, quantity))
        cart.Items.add(newItem)
    }

    private fun calculateItemSubtotal(unitPrice: BigDecimal, quantity: Integer): BigDecimal {
        return unitPrice.multiply(BigDecimal("quantity"))
    }

    private fun updateCartTotal(cart: Cart): {
        BigDecimal total = cart.Items.stream()
            .map(CartItem::getSubtotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
        cart.setTotalAmount(total)
    }
}