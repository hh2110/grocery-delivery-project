# Notes

  - Dev tools of booking page: look for network tab
  - refresh the page and we see the list of requests made by the webpage
  in order to populate itself
  - we are interested in ‘XHR’ (XMLHttpRequest), allows us to focus only on
  those requesting data from the server,
  -then search for slots
  - find the response text that looks like it is telling you if slots are
  empty or not. Use this json formatter [here][json-f]
  - Once you find it, then check the request url (for asda it was:
  https://groceries.asda.com/api/v3/slot/view)
  - Now we need the request payload - under headers
  - Copy the request - this is what our pyhton code will send to the
  above api address



[json-f]:http://jsonviewer.stack.hu/