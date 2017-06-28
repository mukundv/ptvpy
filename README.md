Unofficial Python wrapper for Public Transport Victoria API
Read the full API documentation here: http://stevage.github.io/PTV-API-doc/

Documentation in "quotes" here is verbatim from PTV.
Source: Licensed from Public Transport Victoria under a Creative Commons Attribution 3.0 Australia Licence.

This Python module itself is licensed under WTFPL.

To use it, rename the included apikey.example to apikey.py and include your API key and DevID.

Don't have one? Email APIKeyRequest@ptv.vic.gov.au with subject "PTV Timetable API - request for key"

**Changes**
1. Changed to the new [V3 API](timetableapi.ptv.vic.gov.au/swagger/ui/index)
* replaced ```transportPOIsByMap``` with ```search```
* replaced ```broadNextDepartures``` with ```departures```
2. Changed to Python3