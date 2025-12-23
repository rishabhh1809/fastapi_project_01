events_handler = {
    "POST": {
        "summary": "Create Event",
        "description": "Create a new event. Admin only.",
        "openapi_extra": {
            "requestBody": {
                "content": {
                    "application/json": {
                        "examples": {
                            "create_event": {
                                "summary": "Create Event Example",
                                "value": {
                                    "title": "Tech Conference 2025",
                                    "description": "Annual technology conference",
                                    "date": "2025-06-15T09:00:00Z",
                                    "venue": "Convention Center",
                                    "total_seats": 500,
                                    "price": 99.99,
                                },
                            }
                        }
                    }
                }
            }
        },
    },
    "GET": {
        "summary": "List Events",
        "description": "Get all events with pagination.",
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
    "PUT": {
        "summary": "Update Event",
        "description": "Update an existing event. Admin only.",
        "openapi_extra": {
            "requestBody": {
                "content": {
                    "application/json": {
                        "examples": {
                            "update_event": {
                                "summary": "Update Event Example",
                                "value": {
                                    "title": "Updated Event Title",
                                    "total_seats": 600,
                                },
                            }
                        }
                    }
                }
            }
        },
    },
    "DELETE": {
        "summary": "Delete Event",
        "description": "Delete an event. Admin only.",
        "openapi_extra": {},
    },
}

event_detail_handler = {
    "GET": {
        "summary": "Get Event Details",
        "description": "Get details of a specific event by ID.",
        "openapi_extra": {},
    },
    "PUT": {
        "summary": "Update Event",
        "description": "Update a specific event by ID. Admin only.",
        "openapi_extra": {},
    },
    "DELETE": {
        "summary": "Delete Event",
        "description": "Delete a specific event by ID. Admin only.",
        "openapi_extra": {},
    },
}

available_events_handler = {
    "GET": {
        "summary": "Get Available Events",
        "description": "Get all events with available seats.",
        "openapi_extra": {},
    }
}
