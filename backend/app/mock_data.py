MOCK_ACCOUNTS = {
    "CUST-4492": {
        "customer_id": "CUST-4492",
        "name": "Sarah Chen",
        "email": "sarah.chen@email.com",
        "account_type": "premium",
        "account_status": "active",
        "balance": 15420.50,
        "member_since": "2021-03-14",
        "flags": [],
        "feature_restrictions": []
    },
    "CUST-2201": {
        "customer_id": "CUST-2201",
        "name": "James Okafor",
        "email": "james.okafor@email.com",
        "account_type": "basic",
        "account_status": "active",
        "balance": 3200.00,
        "member_since": "2023-07-22",
        "flags": ["fraud_suspicion"],
        "feature_restrictions": ["cannot_send_international_transfers"]
    },
    "CUST-7733": {
        "customer_id": "CUST-7733",
        "name": "Maria Garcia",
        "email": "maria.garcia@email.com",
        "account_type": "business",
        "account_status": "active",
        "balance": 89200.00,
        "member_since": "2022-01-10",
        "flags": [],
        "feature_restrictions": []
    }
}


RATES_COMMISSIONS = {
    "basic": {
        "account_type": "basic",
        "monthly_maintenance_fee": 0.00,
        "atm_withdrawal_fee": 1.50,
        "international_transfer_fee_pct": 2.5,
        "domestic_transfer_fee": 0.50,
        "overdraft_interest_rate_pct": 18.0,
        "savings_interest_rate_pct": 0.5,
        "card_replacement_fee": 5.00
    },
    "premium": {
        "account_type": "premium",
        "monthly_maintenance_fee": 12.00,
        "atm_withdrawal_fee": 0.00,
        "international_transfer_fee_pct": 1.0,
        "domestic_transfer_fee": 0.00,
        "overdraft_interest_rate_pct": 12.0,
        "savings_interest_rate_pct": 2.0,
        "card_replacement_fee": 0.00,
        "bonus_features": ["Priority support", "Travel insurance", "Cashback 1%"]
    },
    "business": {
        "account_type": "business",
        "monthly_maintenance_fee": 25.00,
        "atm_withdrawal_fee": 0.00,
        "international_transfer_fee_pct": 0.8,
        "domestic_transfer_fee": 0.25,
        "overdraft_interest_rate_pct": 10.0,
        "savings_interest_rate_pct": 1.5,
        "card_replacement_fee": 0.00,
        "bonus_features": ["Multi-user access", "API access", "Dedicated account manager"],
        "payroll_processing_fee": 2.00
    },
    "student": {
        "account_type": "student",
        "monthly_maintenance_fee": 0.00,
        "atm_withdrawal_fee": 0.00,
        "international_transfer_fee_pct": 2.0,
        "domestic_transfer_fee": 0.00,
        "overdraft_interest_rate_pct": 0.0,
        "savings_interest_rate_pct": 1.0,
        "card_replacement_fee": 0.00,
        "bonus_features": ["No minimum balance", "Educational resources"]
    }
}


FAQ_ENTRIES = {
    "transfers": [
        {"question": "How long do domestic transfers take?",
         "answer": "Domestic transfers are processed within 1-2 business days. "
                   "Instant transfers between same-bank accounts are completed within seconds."},
        {"question": "What is the limit for international transfers?",
         "answer": "International transfer limits vary by account type: Basic ($2,500/day), "
                   "Premium ($10,000/day), Business ($50,000/day)."},
        {"question": "How can I cancel a transfer?",
         "answer": "Transfers can be cancelled within 30 minutes of submission via the app. "
                   "After that, please contact support immediately."}
    ],
    "accounts": [
        {"question": "How do I open a new account?",
         "answer": "You can open a new account through our mobile app in under 5 minutes. "
                   "You'll need your ID, proof of address, and a selfie for verification."},
        {"question": "What is the minimum balance requirement?",
         "answer": "Basic and Student accounts have no minimum balance requirement. "
                   "Premium accounts require a minimum of $1,000. "
                   "Business accounts require $5,000."}
    ],
    "limits": [
        {"question": "What is my daily withdrawal limit?",
         "answer": "Daily ATM withdrawal limits: Basic ($500), Premium ($2,000), Business ($5,000). "
                   "These can be temporarily increased by request."},
        {"question": "Is there a limit on mobile payments?",
         "answer": "Mobile payment limits are $1,000 per transaction and $3,000 per day "
                   "for all account types."}
    ],
    "general": [
        {"question": "What are your customer service hours?",
         "answer": "Customer service is available 24/7 via chat, email, and phone. "
                   "Premium and Business customers have access to a dedicated support line."},
        {"question": "How do I report a lost or stolen card?",
         "answer": "Report immediately through the app using 'Lock Card' or call our "
                   "emergency line at 1-800-555-0199. You'll receive a replacement within 3-5 business days."}
    ]
}


SECURITY_POLICIES = {
    "fraud_prevention": {
        "policy_name": "Fraud Prevention and Detection",
        "policy_url": "https://fintech.example.com/policies/fraud-prevention",
        "summary": "We use real-time monitoring and machine learning to detect "
                   "suspicious transactions. Accounts showing unusual patterns "
                   "are temporarily restricted pending verification.",
        "customer_rights": [
            "Request a review of any flagged transaction within 30 days",
            "Receive notification of suspicious activity via SMS and email",
            "Dispute unauthorized transactions and receive provisional credit"
        ],
        "procedures": [
            "Enable two-factor authentication for all transactions",
            "Set transaction alerts for amounts above your preferred threshold",
            "Review your transaction history regularly in the app"
        ]
    },
    "unauthorized_transactions": {
        "policy_name": "Unauthorized Transaction Resolution",
        "policy_url": "https://fintech.example.com/policies/unauthorized-transactions",
        "summary": "If you notice a transaction you did not authorize, report it "
                   "immediately. Your liability for unauthorized transactions is $0 "
                   "if reported within 24 hours.",
        "customer_rights": [
            "Zero liability for unauthorized transactions reported within 24 hours",
            "Limited liability ($50) if reported within 3 business days",
            "Provisional credit within 10 business days of dispute filing"
        ],
        "procedures": [
            "Lock your account immediately via the app",
            "Contact customer service at 1-800-555-0199",
            "File a formal dispute within the app",
            "Monitor accounts for additional suspicious activity"
        ]
    },
    "account_protection": {
        "policy_name": "Account Protection and Security",
        "policy_url": "https://fintech.example.com/policies/account-protection",
        "summary": "We employ bank-grade encryption and multiple security layers "
                   "to protect your account. You can enable additional security "
                   "features through your account settings.",
        "recommended_actions": [
            "Use a strong, unique password",
            "Enable biometric authentication",
            "Set up two-factor authentication",
            "Review active sessions and devices regularly",
            "Never share your PIN or passwords"
        ]
    },
    "data_security": {
        "policy_name": "Data Security Standards",
        "policy_url": "https://fintech.example.com/policies/data-security",
        "summary": "All data is encrypted at rest (AES-256) and in transit (TLS 1.3). "
                   "We comply with PCI DSS, GDPR, and local data protection regulations.",
        "standards": [
            "End-to-end encryption for all communications",
            "Regular third-party security audits",
            "SOC 2 Type II certified",
            "Annual penetration testing"
        ]
    }
}


LEGAL_TERMS = {
    "terms_of_service": {
        "document_name": "Terms of Service",
        "document_url": "https://fintech.example.com/legal/terms-of-service",
        "last_updated": "2025-12-01",
        "sections": [
            {
                "title": "Account Registration",
                "content": "You must provide accurate and complete information "
                           "when creating an account. You are responsible for "
                           "maintaining the confidentiality of your credentials."
            },
            {
                "title": "Usage Restrictions",
                "content": "Accounts may only be used for lawful purposes. "
                           "Any attempt to bypass security measures, conduct "
                           "fraudulent transactions, or use the service for "
                           "money laundering will result in immediate account "
                           "termination."
            },
            {
                "title": "Service Availability",
                "content": "We strive for 99.9% uptime but do not guarantee "
                           "uninterrupted service. Scheduled maintenance will "
                           "be communicated at least 24 hours in advance."
            },
            {
                "title": "Limitation of Liability",
                "content": "Our liability is limited to the amount of the "
                           "transaction in question, or $100, whichever is "
                           "greater. We are not liable for indirect damages "
                           "or losses caused by third-party services."
            }
        ]
    },
    "terms_of_use": {
        "document_name": "Terms of Use",
        "document_url": "https://fintech.example.com/legal/terms-of-use",
        "last_updated": "2025-11-15",
        "sections": [
            {
                "title": "Acceptance",
                "content": "By using our services, you agree to these terms. "
                           "If you do not agree, do not use the service."
            },
            {
                "title": "Modifications",
                "content": "We reserve the right to modify these terms with "
                           "30 days notice. Continued use after changes "
                           "constitutes acceptance."
            }
        ]
    },
    "service_agreement": {
        "document_name": "Service Agreement",
        "document_url": "https://fintech.example.com/legal/service-agreement",
        "last_updated": "2025-10-01",
        "sections": [
            {
                "title": "Services Provided",
                "content": "We provide digital banking services including "
                           "account management, fund transfers, payment "
                           "processing, and financial management tools."
            },
            {
                "title": "Fees and Charges",
                "content": "All applicable fees are disclosed in the Rates "
                           "and Commissions schedule. We reserve the right "
                           "to change fees with 15 days notice."
            },
            {
                "title": "Termination",
                "content": "Either party may terminate this agreement with "
                           "7 days notice. We may terminate immediately for "
                           "violation of terms or suspicious activity."
            }
        ]
    }
}


PRIVACY_POLICY = {
    "data_collection": {
        "section": "Data Collection",
        "document_url": "https://fintech.example.com/privacy/data-collection",
        "summary": "We collect personal information you provide (name, address, "
                   "ID documents), transaction data, device information, and "
                   "usage patterns to provide and improve our services.",
        "data_collected": [
            "Full name and contact information",
            "Government-issued ID documents",
            "Transaction history and patterns",
            "Device information and IP addresses",
            "Location data (with permission)",
            "Biometric data (fingerprint, face ID)"
        ]
    },
    "data_usage": {
        "section": "Data Usage",
        "document_url": "https://fintech.example.com/privacy/data-usage",
        "summary": "Your data is used to process transactions, prevent fraud, "
                   "improve services, and comply with legal obligations.",
        "purposes": [
            "Process and facilitate transactions",
            "Detect and prevent fraud",
            "Improve our products and services",
            "Comply with legal and regulatory requirements",
            "Send service-related communications"
        ]
    },
    "data_sharing": {
        "section": "Data Sharing",
        "document_url": "https://fintech.example.com/privacy/data-sharing",
        "summary": "We only share your data with your consent or as required "
                   "by law. We never sell your personal information.",
        "third_parties": [
            "Payment processors (transaction processing)",
            "Credit bureaus (credit checks with your consent)",
            "Regulatory authorities (legal obligations)",
            "Fraud prevention services (fraud detection)"
        ]
    },
    "user_rights": {
        "section": "Your Rights",
        "document_url": "https://fintech.example.com/privacy/user-rights",
        "summary": "You have the right to access, correct, delete, and port "
                   "your data. You can manage most preferences directly in the app.",
        "rights": [
            "Right to access your personal data",
            "Right to correct inaccurate data",
            "Right to delete your data (subject to legal retention)",
            "Right to data portability",
            "Right to withdraw consent",
            "Right to lodge a complaint with your data protection authority"
        ]
    },
    "data_retention": {
        "section": "Data Retention",
        "document_url": "https://fintech.example.com/privacy/data-retention",
        "summary": "We retain your data for as long as your account is active "
                   "and for 5 years after closure to comply with regulations.",
        "retention_periods": [
            "Account data: Duration of account + 5 years",
            "Transaction records: 7 years",
            "Communication records: 3 years",
            "Marketing preferences: Until consent withdrawn"
        ]
    }
}
