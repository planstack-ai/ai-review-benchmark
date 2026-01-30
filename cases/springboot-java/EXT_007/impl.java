package com.example.ecommerce.service;

import com.example.ecommerce.entity.Order;
import com.example.ecommerce.repository.OrderRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
public class ReportExportService {

    private static final Logger logger = LoggerFactory.getLogger(ReportExportService.class);

    @Value("${app.reports.directory:/app/reports}")
    private String reportsDirectory;

    @Autowired
    private OrderRepository orderRepository;

    public String generateOrderReport(Long userId, String filename) throws IOException {
        List<Order> orders = orderRepository.findByUserId(userId);

        File outputFile = new File(reportsDirectory, filename);

        try (FileWriter writer = new FileWriter(outputFile)) {
            writer.write("Order ID,Date,Status,Total\n");
            for (Order order : orders) {
                writer.write(String.format("%d,%s,%s,%d\n",
                        order.getId(),
                        order.getCreatedAt(),
                        order.getStatus(),
                        order.getTotalCents()));
            }
        }

        logger.info("Generated report: {}", outputFile.getAbsolutePath());
        return outputFile.getName();
    }

    public Resource downloadReport(String filename) {
        File file = new File(reportsDirectory, filename);

        if (!file.exists()) {
            throw new IllegalArgumentException("Report not found: " + filename);
        }

        return new FileSystemResource(file);
    }

    public void deleteReport(String filename) throws IOException {
        File file = new File(reportsDirectory, filename);
        Files.deleteIfExists(file.toPath());
        logger.info("Deleted report: {}", filename);
    }

    public String generateSalesReport(String reportName, LocalDateTime startDate, LocalDateTime endDate)
            throws IOException {

        List<Order> orders = orderRepository.findByCreatedAtBetween(startDate, endDate);

        String filename = reportName + "_" +
                startDate.format(DateTimeFormatter.ISO_DATE) + "_" +
                endDate.format(DateTimeFormatter.ISO_DATE) + ".csv";

        File outputFile = new File(reportsDirectory + "/" + filename);

        try (FileWriter writer = new FileWriter(outputFile)) {
            writer.write("Date,Orders,Revenue\n");

            long totalRevenue = orders.stream()
                    .mapToLong(Order::getTotalCents)
                    .sum();

            writer.write(String.format("%s to %s,%d,%d\n",
                    startDate.toLocalDate(),
                    endDate.toLocalDate(),
                    orders.size(),
                    totalRevenue));
        }

        return filename;
    }

    public byte[] readReportContent(String filename) throws IOException {
        File file = new File(reportsDirectory, filename);
        return Files.readAllBytes(file.toPath());
    }

    public List<String> listUserReports(String userDirectory) {
        File dir = new File(reportsDirectory, userDirectory);
        String[] files = dir.list();
        return files != null ? List.of(files) : List.of();
    }
}
