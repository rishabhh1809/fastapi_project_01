bookings_handler = {
    "POST": {
        "summary": "Create Booking",
        "description": "Create a new booking for an event. Requires authentication.",
        "openapi_extra": {
            "requestBody": {
                "content": {
                    "application/json": {
                        "examples": {
                            "create_booking": {
                                "summary": "Create Booking Example",
                                "value": {"event_id": 1, "quantity": 2},
                            }
                        }
                    }
                }
            }
        },
    },
    "GET": {
        "summary": "List User Bookings",
        "description": "Get all bookings for the authenticated user.",
        "openapi_extra": {
            "parameters": [
                {
                    "name": "skip",
                    "in": "query",
                    "description": "Number of records to skip",
                    "required": False,
                    "schema": {"type": "integer", "default": 0},
                },
                {
                    "name": "limit",
                    "in": "query",
                    "description": "Maximum number of records to return",
                    "required": False,
                    "schema": {"type": "integer", "default": 100},
                },
            ]
        },
    },
    "DELETE": {
        "summary": "Cancel Booking",
        "description": "Cancel a booking. Users can only cancel their own bookings.",
        "openapi_extra": {},
    },
}

booking_detail_handler = {
    "GET": {
        "summary": "Get Booking Details",
        "description": "Get details of a specific booking.",
        "openapi_extra": {},
    },
    "DELETE": {
        "summary": "Cancel Booking",
        "description": "Cancel a specific booking.",
        "openapi_extra": {},
    },
}

admin_bookings_handler = {
    "GET": {
        "summary": "Get All Bookings (Admin)",
        "description": "Get all bookings in the system. Admin only.",
        "openapi_extra": {},
    }
}

event_bookings_handler = {
    "GET": {
        "summary": "Get Event Bookings (Admin)",
        "description": "Get all bookings for a specific event. Admin only.",
        "openapi_extra": {},
    }
}
