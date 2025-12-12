/**
 * M365 Security Toolkit - Data Loader
 * Fetches and processes audit data from JSON API
 * Version: 1.0.0
 */

(function() {
    'use strict';

    const DATA_LOADER = {
        // Configuration
        config: {
            apiEndpoint: './api/sample-audit.json',
            cacheTimeout: 5 * 60 * 1000, // 5 minutes
            retryAttempts: 3,
            retryDelay: 1000
        },

        // Cache
        cache: {
            data: null,
            timestamp: null
        },

        /**
         * Fetch audit data with caching and retry logic
         * @returns {Promise<Object>} Audit data
         */
        async fetchAuditData() {
            // Check cache first
            if (this.isCacheValid()) {
                console.log('Using cached audit data');
                return this.cache.data;
            }

            // Fetch fresh data
            try {
                const data = await this.fetchWithRetry(this.config.apiEndpoint);
                
                // Update cache
                this.cache.data = data;
                this.cache.timestamp = Date.now();
                
                return data;
            } catch (error) {
                console.error('Failed to fetch audit data:', error);
                
                // Fallback to cached data if available
                if (this.cache.data) {
                    console.warn('Using stale cached data due to fetch error');
                    return this.cache.data;
                }
                
                // Use sample data as last resort
                return this.getSampleData();
            }
        },

        /**
         * Check if cached data is still valid
         * @returns {boolean}
         */
        isCacheValid() {
            if (!this.cache.data || !this.cache.timestamp) {
                return false;
            }

            const age = Date.now() - this.cache.timestamp;
            return age < this.config.cacheTimeout;
        },

        /**
         * Fetch with retry logic
         * @param {string} url - URL to fetch
         * @returns {Promise<Object>}
         */
        async fetchWithRetry(url, attempt = 1) {
            try {
                const response = await fetch(url, {
                    headers: {
                        'Accept': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                return await response.json();
            } catch (error) {
                if (attempt < this.config.retryAttempts) {
                    console.log(`Retry attempt ${attempt} of ${this.config.retryAttempts}`);
                    await this.delay(this.config.retryDelay * attempt);
                    return this.fetchWithRetry(url, attempt + 1);
                }
                throw error;
            }
        },

        /**
         * Delay utility
         * @param {number} ms - Milliseconds to delay
         * @returns {Promise}
         */
        delay(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        },

        /**
         * Process audit data and calculate statistics
         * @param {Array} auditResults - Array of audit controls
         * @returns {Object} Processed statistics
         */
        processAuditData(auditResults) {
            if (!Array.isArray(auditResults)) {
                console.error('Invalid audit results format');
                return this.getEmptyStats();
            }

            const stats = {
                total: auditResults.length,
                passed: 0,
                failed: 0,
                manual: 0,
                critical: 0,
                high: 0,
                medium: 0,
                low: 0,
                passRate: 0,
                failRate: 0,
                byCategory: {},
                recentChanges: []
            };

            auditResults.forEach(control => {
                // Count by status
                const status = (control.Status || '').toLowerCase();
                if (status === 'pass') stats.passed++;
                else if (status === 'fail') stats.failed++;
                else if (status === 'manual') stats.manual++;

                // Count by severity
                const severity = (control.Severity || '').toLowerCase();
                if (severity === 'critical') stats.critical++;
                else if (severity === 'high') stats.high++;
                else if (severity === 'medium') stats.medium++;
                else if (severity === 'low') stats.low++;

                // Group by category (extract from ControlId)
                const category = this.extractCategory(control.ControlId);
                if (!stats.byCategory[category]) {
                    stats.byCategory[category] = {
                        total: 0,
                        passed: 0,
                        failed: 0,
                        manual: 0
                    };
                }
                stats.byCategory[category].total++;
                stats.byCategory[category][status]++;
            });

            // Calculate rates
            if (stats.total > 0) {
                stats.passRate = ((stats.passed / stats.total) * 100).toFixed(1);
                stats.failRate = ((stats.failed / stats.total) * 100).toFixed(1);
            }

            return stats;
        },

        /**
         * Extract category from control ID
         * @param {string} controlId - Control ID (e.g., "1.1.1")
         * @returns {string} Category name
         */
        extractCategory(controlId) {
            if (!controlId) return 'Unknown';
            
            const parts = controlId.split('.');
            if (parts.length === 0) return 'Unknown';
            
            const categoryMap = {
                '1': 'Exchange Online',
                '2': 'Azure AD',
                '3': 'Microsoft Teams',
                '4': 'SharePoint Online',
                '5': 'OneDrive',
                '6': 'Security & Compliance',
                '7': 'Microsoft Defender'
            };
            
            return categoryMap[parts[0]] || `Category ${parts[0]}`;
        },

        /**
         * Filter audit data by criteria
         * @param {Array} auditResults - Audit controls
         * @param {Object} filters - Filter criteria
         * @returns {Array} Filtered results
         */
        filterAuditData(auditResults, filters) {
            if (!filters || Object.keys(filters).length === 0) {
                return auditResults;
            }

            return auditResults.filter(control => {
                // Filter by status
                if (filters.status && filters.status.length > 0) {
                    if (!filters.status.includes(control.Status.toLowerCase())) {
                        return false;
                    }
                }

                // Filter by severity
                if (filters.severity && filters.severity.length > 0) {
                    if (!filters.severity.includes(control.Severity.toLowerCase())) {
                        return false;
                    }
                }

                // Filter by category
                if (filters.category) {
                    const category = this.extractCategory(control.ControlId);
                    if (category !== filters.category) {
                        return false;
                    }
                }

                // Filter by search term
                if (filters.search) {
                    const searchLower = filters.search.toLowerCase();
                    const searchableText = [
                        control.ControlId,
                        control.Title,
                        control.Expected,
                        control.Actual
                    ].join(' ').toLowerCase();
                    
                    if (!searchableText.includes(searchLower)) {
                        return false;
                    }
                }

                return true;
            });
        },

        /**
         * Get sample data as fallback
         * @returns {Array} Sample audit controls
         */
        getSampleData() {
            return [
                {
                    ControlId: "1.1.1",
                    Title: "Ensure modern authentication for Exchange Online is enabled",
                    Severity: "High",
                    Status: "Pass",
                    Expected: "Modern authentication enabled",
                    Actual: "Modern authentication is enabled",
                    Evidence: "OAuth2ClientProfileEnabled=True",
                    Reference: "CIS Microsoft 365 Foundations Benchmark v3.0.0",
                    Timestamp: new Date().toISOString()
                },
                {
                    ControlId: "1.1.3",
                    Title: "Ensure the admin consent workflow is enabled",
                    Severity: "Medium",
                    Status: "Fail",
                    Expected: "Admin consent workflow enabled",
                    Actual: "Admin consent workflow is not enabled",
                    Evidence: "AdminConsentRequestWorkflow.IsEnabled=False",
                    Reference: "CIS Microsoft 365 Foundations Benchmark v3.0.0",
                    Timestamp: new Date().toISOString()
                },
                {
                    ControlId: "2.1.1",
                    Title: "Ensure Security Defaults is enabled",
                    Severity: "High",
                    Status: "Pass",
                    Expected: "Security defaults enabled or equivalent policies",
                    Actual: "Security defaults enabled",
                    Evidence: "SecurityDefaults.IsEnabled=True",
                    Reference: "CIS Microsoft 365 Foundations Benchmark v3.0.0",
                    Timestamp: new Date().toISOString()
                }
            ];
        },

        /**
         * Get empty statistics object
         * @returns {Object}
         */
        getEmptyStats() {
            return {
                total: 0,
                passed: 0,
                failed: 0,
                manual: 0,
                critical: 0,
                high: 0,
                medium: 0,
                low: 0,
                passRate: 0,
                failRate: 0,
                byCategory: {},
                recentChanges: []
            };
        },

        /**
         * Sort audit data
         * @param {Array} auditResults - Audit controls
         * @param {string} sortBy - Field to sort by
         * @param {string} order - 'asc' or 'desc'
         * @returns {Array} Sorted results
         */
        sortAuditData(auditResults, sortBy = 'ControlId', order = 'asc') {
            const sorted = [...auditResults].sort((a, b) => {
                let aVal = a[sortBy];
                let bVal = b[sortBy];

                // Handle string comparison
                if (typeof aVal === 'string') {
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                }

                if (aVal < bVal) return order === 'asc' ? -1 : 1;
                if (aVal > bVal) return order === 'asc' ? 1 : -1;
                return 0;
            });

            return sorted;
        },

        /**
         * Export data to CSV
         * @param {Array} auditResults - Audit controls
         * @returns {string} CSV string
         */
        exportToCSV(auditResults) {
            const headers = ['ControlId', 'Title', 'Severity', 'Status', 'Expected', 'Actual', 'Evidence'];
            const rows = auditResults.map(control => 
                headers.map(header => {
                    const value = control[header] || '';
                    // Escape quotes and wrap in quotes if contains comma
                    return value.includes(',') ? `"${value.replace(/"/g, '""')}"` : value;
                })
            );

            return [
                headers.join(','),
                ...rows.map(row => row.join(','))
            ].join('\n');
        },

        /**
         * Download data as file
         * @param {string} content - File content
         * @param {string} filename - File name
         * @param {string} mimeType - MIME type
         */
        downloadFile(content, filename, mimeType = 'text/plain') {
            const blob = new Blob([content], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        }
    };

    // Expose globally
    window.DataLoader = DATA_LOADER;

})();
