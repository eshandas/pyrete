class Keys(object):
    DATABASE_CONNECTION = 'database_connection'


class SuccessMessages(object):
    ADD_RULES_SUCCESS = 'Added rule successfully'
    UPDATE_RULES_SUCCESS = 'Updated rule successfully'
    DELETE_RULES_SUCCESS = 'Deleted rule successfully'
    PROCESS_STARTED_SUCCESSFULLY = 'A process has started up successfully'
    RULE_PROCESSED_SUCCESSFULLY = 'A rule was processed successfully'
    DATABASE_DETAILS_SAVED = 'The database details were saved successfully'


class FailMessages(object):
    USER_INACTIVE = 'This user is not active.'
    INVALID_CREDENTIALS = 'Wrong username/password'
    INVALID_COLLECTION = 'Invalid collection'
    INVALID_KEY = 'The rule key/collection is either empty or invalid'
    KEY_EXIST = 'Rule with this key exist',
    INVALID_INPUT = 'Invalid input'
    INVALID_DATABASE_DETAILS = 'Invalid database details'


class RequestKeys(object):
    RULES = 'rules'
    KEY = 'key'
    WEBHOOK_DATA = 'webhookData'
    DESCRIPTION = 'description'
    BACKGROUND_PROCESS = 'backgroundProcess'
    COLLECTION = 'collections'
    ID = 'id'
    RULE_KEY = 'key'
    NAME = 'name'
    DATABASE_TYPE = 'databaseType'
    CONNECTION = 'connection'


class ResponseKeys(object):
    DATA = 'data'
    IS_COMPLETED = 'isCompleted'
    ITEMS_PASSED = 'itemsPassed'


class DummyData(object):
    FIELDS = [
        "subtotal_price",
        "buyer_accepts_marketing",
        "reference",
        "shipping_lines",
        "cart_token",
        "updated_at",
        "taxes_included",
        "currency",
        "discount_codes",
        "total_weight",
        "source_name",
        "closed_at",
        "processed_at",
        "payment_gateway_names",
        "location_id",
        "gateway",
        "order_status_url",
        "confirmed",
        "user_id",
        "fulfillments",
        "landing_site_ref",
        "customer_locale",
        "source_identifier",
        "id",
        "note",
        "landing_site",
        "browser_ip",
        "total_line_items_price",
        "cancelled_at",
        "test",
        "email",
        "total_tax",
        "billing_address",
        "billing_address.province",
        "billing_address.city",
        "billing_address.first_name",
        "billing_address.last_name",
        "billing_address.name",
        "billing_address.zip",
        "billing_address.province_code",
        "billing_address.address1",
        "billing_address.address2",
        "billing_address.longitude",
        "billing_address.phone",
        "billing_address.country_code",
        "billing_address.country",
        "billing_address.latitude",
        "billing_address.company",
        "cancel_reason",
        "tax_lines",
        "tags",
        "financial_status",
        "phone",
        "total_discounts",
        "number",
        "checkout_id",
        "processing_method",
        "device_id",
        "customer",
        "customer.total_spent",
        "customer.multipass_identifier",
        "customer.first_name",
        "customer.last_name",
        "customer.orders_count",
        "customer.created_at",
        "customer.tags",
        "customer.updated_at",
        "customer.last_order_id",
        "customer.id",
        "customer.note",
        "customer.phone",
        "customer.state",
        "customer.default_address",
        "customer.default_address.province",
        "customer.default_address.city",
        "customer.default_address.first_name",
        "customer.default_address.last_name",
        "customer.default_address.name",
        "customer.default_address.zip",
        "customer.default_address.province_code",
        "customer.default_address.default",
        "customer.default_address.address1",
        "customer.default_address.address2",
        "customer.default_address.id",
        "customer.default_address.phone",
        "customer.default_address.country_code",
        "customer.default_address.country",
        "customer.default_address.country_name",
        "customer.default_address.customer_id",
        "customer.default_address.company",
        "customer.tax_exempt",
        "customer.accepts_marketing",
        "customer.email",
        "customer.last_order_name",
        "customer.verified_email",
        "line_items",
        "line_items.requires_shipping",
        "line_items.variant_id",
        "line_items.id",
        "line_items.product_exists",
        "line_items.sku",
        "line_items.title",
        "line_items.fulfillment_service",
        "line_items.total_discount",
        "line_items.variant_title",
        "line_items.vendor",
        "line_items.tax_lines",
        "line_items.price",
        "line_items.taxable",
        "line_items.properties",
        "line_items.product_id",
        "line_items.fulfillable_quantity",
        "line_items.name",
        "line_items.gift_card",
        "line_items.fulfillment_status",
        "line_items.variant_inventory_management",
        "line_items.grams",
        "line_items.quantity",
        "total_price",
        "name",
        "refunds",
        "checkout_token",
        "created_at",
        "referring_site",
        "note_attributes",
        "note_attributes.name",
        "note_attributes.value",
        "fulfillment_status",
        "total_price_usd",
        "source_url",
        "shipping_address",
        "shipping_address.province",
        "shipping_address.city",
        "shipping_address.first_name",
        "shipping_address.last_name",
        "shipping_address.name",
        "shipping_address.zip",
        "shipping_address.province_code",
        "shipping_address.address1",
        "shipping_address.address2",
        "shipping_address.longitude",
        "shipping_address.phone",
        "shipping_address.country_code",
        "shipping_address.country",
        "shipping_address.latitude",
        "shipping_address.company",
        "contact_email",
        "_id",
        "order_number",
        "token"
    ]

