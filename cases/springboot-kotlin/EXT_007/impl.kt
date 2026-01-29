package com.example.ecommerce.service

import com.example.ecommerce.entity.Order
import com.example.ecommerce.repository.OrderRepository
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.FileSystemResource
import org.springframework.core.io.Resource
import org.springframework.stereotype.Service
import java.io.File
import java.io.FileWriter
import java.nio.file.Files
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@Service
class ReportExportService(
    private val orderRepository: OrderRepository
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Value("\${app.reports.directory:/app/reports}")
    private lateinit var reportsDirectory: String

    fun generateOrderReport(userId: Long, filename: String): String {
        val orders = orderRepository.findByUserId(userId)

        val outputFile = File(reportsDirectory, filename)

        FileWriter(outputFile).use { writer ->
            writer.write("Order ID,Date,Status,Total\n")
            orders.forEach { order ->
                writer.write("${order.id},${order.createdAt},${order.status},${order.totalCents}\n")
            }
        }

        logger.info("Generated report: ${outputFile.absolutePath}")
        return outputFile.name
    }

    fun downloadReport(filename: String): Resource {
        val file = File(reportsDirectory, filename)

        if (!file.exists()) {
            throw IllegalArgumentException("Report not found: $filename")
        }

        return FileSystemResource(file)
    }

    fun deleteReport(filename: String) {
        val file = File(reportsDirectory, filename)
        Files.deleteIfExists(file.toPath())
        logger.info("Deleted report: $filename")
    }

    fun generateSalesReport(reportName: String, startDate: LocalDateTime, endDate: LocalDateTime): String {
        val orders = orderRepository.findByCreatedAtBetween(startDate, endDate)

        val filename = "${reportName}_${startDate.format(DateTimeFormatter.ISO_DATE)}_${endDate.format(DateTimeFormatter.ISO_DATE)}.csv"

        val outputFile = File("$reportsDirectory/$filename")

        FileWriter(outputFile).use { writer ->
            writer.write("Date,Orders,Revenue\n")

            val totalRevenue = orders.sumOf { it.totalCents }

            writer.write("${startDate.toLocalDate()} to ${endDate.toLocalDate()},${orders.size},$totalRevenue\n")
        }

        return filename
    }

    fun readReportContent(filename: String): ByteArray {
        val file = File(reportsDirectory, filename)
        return Files.readAllBytes(file.toPath())
    }

    fun listUserReports(userDirectory: String): List<String> {
        val dir = File(reportsDirectory, userDirectory)
        val files = dir.list()
        return files?.toList() ?: emptyList()
    }
}
