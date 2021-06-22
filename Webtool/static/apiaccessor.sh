#!/bin/bash

token="oLH7C9g5twATAq6yW1PDHIAtAxaXQzNcSj71Az67"
# same as above, but exported using a custom format
curl -H "Authorization: Bearer $token" -H "Content-Type: application/json" \
    https://api.adsabs.harvard.edu/v1/export/custom \
    -X POST \
    -d '{"format": "%m %Y", "bibcode": ["2000A&AS..143...41K", "2000A&AS..143...85A", "2000A&AS..143..111G"]}'