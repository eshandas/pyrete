from pyrete.core.data_layer import DataLayer


mapper = DataLayer()
mapper.get_all_collections()
demo_dict = {
    "subtotal_price": "51.00",
    "billing_address": {
        "province": "North Carolina",
        "city": "Franklinton"
    },
    "note_attributes": [
        {
            "name": "address-type",
            "value": "residential",
        },

        {
            "name": "transit - time",
            "value": "1",
        }
    ],
    "token": "384779c27a35e8fcc0c948ad87f0ac35"
}
mapper.get_collection_fields('orders')
