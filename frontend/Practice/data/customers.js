const customers = [
  {
    id: "CUST001",
    name: "Rahul Sharma",
    tier: "Silver",
    status: "Active",
    birthdayMonth: false,
    doNotContact: false,
    consent: {
      whatsapp: true,
      email: true,
      discord: false
    }
  },
  {
    id: "CUST002",
    name: "Priya Mehta",
    tier: "Potential",
    status: "Inactive",
    birthdayMonth: true,
    doNotContact: false,
    consent: {
      whatsapp: false,
      email: true,
      discord: true
    }
  }
];