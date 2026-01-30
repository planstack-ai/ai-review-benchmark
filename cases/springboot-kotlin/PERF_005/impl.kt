package com.example.ecommerce.service

import com.example.ecommerce.entity.Customer
import com.example.ecommerce.repository.CustomerRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class CustomerSearchService(
    private val customerRepository: CustomerRepository
) {
    @Transactional(readOnly = true)
    fun findByEmail(email: String): Customer? {
        return customerRepository.findByEmail(email)
    }

    @Transactional(readOnly = true)
    fun findByPhoneNumber(phoneNumber: String): List<Customer> {
        val normalizedPhone = normalizePhoneNumber(phoneNumber)
        return customerRepository.findByPhoneNumber(normalizedPhone)
    }

    @Transactional(readOnly = true)
    fun searchByName(searchTerm: String): List<Customer> {
        return customerRepository.findByLastNameContaining(searchTerm)
    }

    @Transactional(readOnly = true)
    fun advancedSearch(email: String?, phone: String?, name: String?): List<Customer> {
        val results = mutableListOf<Customer>()

        email?.takeIf { it.isNotEmpty() }?.let {
            customerRepository.findByEmail(it)?.let { customer -> results.add(customer) }
        }

        phone?.takeIf { it.isNotEmpty() }?.let {
            results.addAll(customerRepository.findByPhoneNumber(normalizePhoneNumber(it)))
        }

        name?.takeIf { it.isNotEmpty() }?.let {
            results.addAll(customerRepository.findByLastNameContaining(it))
        }

        return results.distinctBy { it.id }
    }

    @Transactional(readOnly = true)
    fun findCustomerForSupport(identifier: String): Customer? {
        customerRepository.findByEmail(identifier)?.let { return it }

        val byPhone = customerRepository.findByPhoneNumber(identifier)
        if (byPhone.isNotEmpty()) return byPhone.first()

        val byName = customerRepository.findByLastNameContaining(identifier)
        if (byName.isNotEmpty()) return byName.first()

        return null
    }

    private fun normalizePhoneNumber(phone: String?): String {
        return phone?.replace(Regex("[^0-9+]"), "") ?: ""
    }
}
