const customerServiceTickets = [
  {
    ticketId: "SR-2026-001248",
    customerId: "CRM-000124",
    customerName: "Riya Sharma",
    linkedOrder: "ORD-2026-78421",
    issueCategory: "Delivery Delay",
    queryType: "Complaint",
    priority: "High",
    status: "Open",

    assignedAgentId: "AGT-001",
    assignedTo: "Ankit Kumar",

    createdOn: "02 Jul 2026",
    slaDue: "07 Jul 2026",
    lastUpdated: "02 Jul 2026",
    channel: "WhatsApp",
    city: "Mumbai",
    membershipTier: "Gold",
    customerSegment: "Electronics Buyer",
    churnRisk: "Medium",
    maskedPhone: "98******21",
    maskedEmail: "ri***@gmail.com",

    productName: "Wireless Headphones",
    productCategory: "Electronics",
    orderDate: "29 Jun 2026",
    orderValue: 2499,
    paymentStatus: "Paid",
    deliveryStatus: "Delayed",
    returnRefundStatus: "Not Requested",

    description: "Customer reported delayed delivery and requested urgent update.",
    internalNotes: "Logistics partner contacted. Awaiting revised delivery confirmation.",
    resolutionSummary: "",

    callReview: "",
    contactResult: "Not Contacted",
    followUpRequired: "No",
    followUpDate: "",
    followUpNote: "",
    completedOn: "",
    lastActionBy: "",

    actionHistory: [],
    timeline: [
      {
        title: "Ticket Created",
        date: "02 Jul 2026",
        note: "Complaint received via WhatsApp."
      },
      {
        title: "Assigned to Agent",
        date: "02 Jul 2026",
        note: "Assigned to Ankit Kumar."
      }
    ]
  },

  {
    ticketId: "SR-2026-001249",
    customerId: "CRM-000178",
    customerName: "Kabir Malhotra",
    linkedOrder: "ORD-2026-78432",
    issueCategory: "Payment",
    queryType: "Refund",
    priority: "Critical",
    status: "Escalated",

    assignedAgentId: "AGT-002",
    assignedTo: "Harshit Sharma",

    createdOn: "01 Jul 2026",
    slaDue: "06 Jul 2026",
    lastUpdated: "03 Jul 2026",
    channel: "Email",
    city: "Pune",
    membershipTier: "Platinum",
    customerSegment: "High Value Customer",
    churnRisk: "High",
    maskedPhone: "99******45",
    maskedEmail: "ka***@outlook.com",

    productName: "Smart Watch Pro",
    productCategory: "Wearables",
    orderDate: "28 Jun 2026",
    orderValue: 8999,
    paymentStatus: "Refund Initiated",
    deliveryStatus: "Returned",
    returnRefundStatus: "Refund Pending",

    description: "Customer returned the product but refund has not been credited.",
    internalNotes: "Escalated to finance team for refund confirmation.",
    resolutionSummary: "",

    callReview: "",
    contactResult: "Need Follow-up",
    followUpRequired: "Yes",
    followUpDate: "2026-07-07",
    followUpNote: "Follow up after finance confirmation.",
    completedOn: "",
    lastActionBy: "",

    actionHistory: [],
    timeline: [
      {
        title: "Ticket Created",
        date: "01 Jul 2026",
        note: "Refund complaint received by email."
      },
      {
        title: "Assigned to Agent",
        date: "01 Jul 2026",
        note: "Assigned to Harshit Sharma."
      },
      {
        title: "Escalated",
        date: "03 Jul 2026",
        note: "Escalated to finance due to SLA risk."
      }
    ]
  },

  {
    ticketId: "SR-2026-001250",
    customerId: "CRM-000203",
    customerName: "Ananya Iyer",
    linkedOrder: "ORD-2026-78445",
    issueCategory: "Product Quality",
    queryType: "Complaint",
    priority: "Medium",
    status: "In Progress",

    assignedAgentId: "AGT-001",
    assignedTo: "Ankit Kumar",

    createdOn: "02 Jul 2026",
    slaDue: "08 Jul 2026",
    lastUpdated: "03 Jul 2026",
    channel: "App",
    city: "Bengaluru",
    membershipTier: "Silver",
    customerSegment: "Lifestyle Buyer",
    churnRisk: "Medium",
    maskedPhone: "97******10",
    maskedEmail: "an***@gmail.com",

    productName: "Ceramic Dinner Set",
    productCategory: "Home & Living",
    orderDate: "30 Jun 2026",
    orderValue: 3499,
    paymentStatus: "Paid",
    deliveryStatus: "Delivered",
    returnRefundStatus: "Replacement Requested",

    description: "Customer received damaged dinner set and requested replacement.",
    internalNotes: "Image proof received. Replacement approval pending.",
    resolutionSummary: "",

    callReview: "Customer shared damaged product images and requested replacement.",
    contactResult: "Interested",
    followUpRequired: "Yes",
    followUpDate: "2026-07-08",
    followUpNote: "Update customer after replacement approval.",
    completedOn: "",
    lastActionBy: "Ankit Kumar",

    actionHistory: [
      {
        actionBy: "Ankit Kumar",
        role: "Customer Service Agent",
        date: "03 Jul 2026",
        previousStatus: "Open",
        newStatus: "In Progress",
        contactResult: "Interested",
        followUpRequired: "Yes",
        followUpDate: "2026-07-08",
        note: "Customer contacted and damage proof collected."
      }
    ],
    timeline: [
      {
        title: "Ticket Created",
        date: "02 Jul 2026",
        note: "Complaint raised through app."
      },
      {
        title: "Customer Contacted",
        date: "03 Jul 2026",
        note: "Damage images collected by Ankit Kumar."
      },
      {
        title: "Follow-up Scheduled",
        date: "03 Jul 2026",
        note: "Follow-up scheduled for 2026-07-08."
      }
    ]
  },

  {
    ticketId: "SR-2026-001251",
    customerId: "CRM-000256",
    customerName: "Dev Patel",
    linkedOrder: "ORD-2026-78458",
    issueCategory: "Return",
    queryType: "Request",
    priority: "Low",
    status: "Waiting for Customer",

    assignedAgentId: "AGT-002",
    assignedTo: "Harshit Sharma",

    createdOn: "30 Jun 2026",
    slaDue: "09 Jul 2026",
    lastUpdated: "02 Jul 2026",
    channel: "SMS",
    city: "Ahmedabad",
    membershipTier: "Bronze",
    customerSegment: "Occasional Buyer",
    churnRisk: "Low",
    maskedPhone: "95******88",
    maskedEmail: "de***@gmail.com",

    productName: "Running Shoes",
    productCategory: "Fashion",
    orderDate: "26 Jun 2026",
    orderValue: 2199,
    paymentStatus: "Paid",
    deliveryStatus: "Delivered",
    returnRefundStatus: "Return Requested",

    description: "Customer requested return due to size mismatch.",
    internalNotes: "Waiting for customer to upload product images.",
    resolutionSummary: "",

    callReview: "",
    contactResult: "No Response",
    followUpRequired: "Yes",
    followUpDate: "2026-07-07",
    followUpNote: "Call customer again for return photos.",
    completedOn: "",
    lastActionBy: "",

    actionHistory: [],
    timeline: [
      {
        title: "Ticket Created",
        date: "30 Jun 2026",
        note: "Return request received."
      },
      {
        title: "Waiting for Customer",
        date: "02 Jul 2026",
        note: "Asked customer for photos."
      }
    ]
  },

  {
    ticketId: "SR-2026-001252",
    customerId: "CRM-000301",
    customerName: "Meera Joshi",
    linkedOrder: "ORD-2026-78470",
    issueCategory: "Do Not Contact Request",
    queryType: "Request",
    priority: "High",
    status: "Resolved",

    assignedAgentId: "AGT-003",
    assignedTo: "Sneha Rao",

    createdOn: "29 Jun 2026",
    slaDue: "01 Jul 2026",
    lastUpdated: "01 Jul 2026",
    channel: "Email",
    city: "Delhi",
    membershipTier: "Gold",
    customerSegment: "Repeat Buyer",
    churnRisk: "Medium",
    maskedPhone: "96******33",
    maskedEmail: "me***@gmail.com",

    productName: "Organic Skin Care Kit",
    productCategory: "Beauty",
    orderDate: "24 Jun 2026",
    orderValue: 1599,
    paymentStatus: "Paid",
    deliveryStatus: "Delivered",
    returnRefundStatus: "Not Requested",

    description: "Customer requested no marketing contact across channels.",
    internalNotes: "Consent withdrawal request completed.",
    resolutionSummary: "Customer marked as Do Not Contact across marketing channels.",

    callReview: "Customer confirmed they do not want promotional communication.",
    contactResult: "Not Interested",
    followUpRequired: "No",
    followUpDate: "",
    followUpNote: "",
    completedOn: "01 Jul 2026",
    lastActionBy: "Sneha Rao",

    actionHistory: [
      {
        actionBy: "Sneha Rao",
        role: "Customer Service Agent",
        date: "01 Jul 2026",
        previousStatus: "In Progress",
        newStatus: "Resolved",
        contactResult: "Not Interested",
        followUpRequired: "No",
        followUpDate: "",
        note: "Consent withdrawal completed."
      }
    ],
    timeline: [
      {
        title: "Ticket Created",
        date: "29 Jun 2026",
        note: "DNC request received by email."
      },
      {
        title: "Consent Updated",
        date: "01 Jul 2026",
        note: "All marketing channels withdrawn."
      },
      {
        title: "Ticket Resolved",
        date: "01 Jul 2026",
        note: "Resolved by Sneha Rao."
      }
    ]
  }
];