define({ "api": [
  {
    "type": "get",
    "url": "/v2/check",
    "title": "Job execution state",
    "version": "0.1.0",
    "name": "GetJob",
    "group": "Job",
    "permission": [
      {
        "name": "none"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "job_id",
            "description": "<p>Unique job identifier</p>"
          }
        ]
      }
    },
    "examples": [
      {
        "title": "Example usage:",
        "content": "curl -X GET \\\n    http://localhost:6565/v2/check?job_id=<job_id>",
        "type": "curl"
      }
    ],
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "json[]",
            "optional": false,
            "field": "body.api_info",
            "description": "<p>Endpoint details</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "body.job_id",
            "description": "<p>Unique job identifier</p>"
          },
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body.progress",
            "description": "<p>Job progress</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "body.progress.state",
            "description": "<p>Job execution status</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "body.progress.return",
            "description": "<p>Job results (if any)</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success body example:",
          "content": "HTTP/1.1 200 OK\n{\n  \"api_info\": {\n    \"method\": \"GET\",\n    \"endpoint\": \"0.0.0.0\",\n    \"path\": \"/v2/check\"\n  },\n  \"job_id\": 4581666186,\n  \"progress\": {\n    \"state\": \"SUCCESS\",\n    \"return\": \"\"\n  }\n}",
          "type": "json"
        }
      ]
    },
    "filename": "server/api.py",
    "groupTitle": "Job"
  },
  {
    "type": "post",
    "url": "/v2/kill",
    "title": "Termine running job",
    "version": "0.1.0",
    "name": "PostJob",
    "group": "Job",
    "permission": [
      {
        "name": "user"
      }
    ],
    "header": {
      "fields": {
        "Header": [
          {
            "group": "Header",
            "type": "String",
            "optional": false,
            "field": "x-api-key",
            "description": "<p>API unique access-key</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "json",
            "optional": false,
            "field": "body",
            "description": ""
          },
          {
            "group": "Parameter",
            "type": "json",
            "optional": false,
            "field": "body.job_id",
            "description": "<p>Unique job identifier</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request body example:",
          "content": "{\n    \"job_id\": \"4581666186\"\n}",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body.api_info",
            "description": "<p>Endpoint details</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "body.job_id",
            "description": "<p>Unique job identifier</p>"
          },
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body.progress",
            "description": "<p>Job progress</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "body.progress.state",
            "description": "<p>Job execution status</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "body.progress.return",
            "description": "<p>Job result (i.e., None)</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success body example:",
          "content": "HTTP/1.1 200 OK\n{\n  \"api_info\": {\n    \"method\": \"POST\",\n    \"endpoint\": \"0.0.0.0\",\n    \"path\": \"/v2/kill\"\n  },\n  \"job_id\": 4581666186,\n  \"progress\": {\n    \"state\": \"REVOKED\",\n    \"return\": null\n  }\n}",
          "type": "json"
        }
      ]
    },
    "filename": "server/api.py",
    "groupTitle": "Job"
  },
  {
    "type": "post",
    "url": "/v2/health",
    "title": "Check API status",
    "version": "0.1.0",
    "name": "GetHealth",
    "group": "System",
    "permission": [
      {
        "name": "none"
      }
    ],
    "success": {
      "examples": [
        {
          "title": "Success body example:",
          "content": "HTTP/1.1 200 OK",
          "type": "http"
        }
      ]
    },
    "filename": "server/api.py",
    "groupTitle": "System"
  },
  {
    "type": "get",
    "url": "/v2/status",
    "title": "Ticket execution state",
    "version": "0.1.0",
    "name": "GetTicket",
    "group": "Ticket",
    "permission": [
      {
        "name": "none"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "ticket_id",
            "description": "<p>Unique ticket identifier</p>"
          }
        ]
      }
    },
    "examples": [
      {
        "title": "Example usage:",
        "content": "curl -X GET \\\n    'http://localhost:6565/v2/status?ticket_id=<ticket_id>'",
        "type": "curl"
      }
    ],
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "json[]",
            "optional": false,
            "field": "body.api_info",
            "description": "<p>Unique ticket identifier</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "body.ticket_id",
            "description": "<p>Unique ticket identifier</p>"
          },
          {
            "group": "Success 200",
            "type": "Date",
            "optional": false,
            "field": "body.created_on",
            "description": "<p>Ticket creation date</p>"
          },
          {
            "group": "Success 200",
            "type": "Date",
            "optional": false,
            "field": "body.updated_on",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Date",
            "optional": false,
            "field": "body.last_access",
            "description": "<p>Last ticket's access date</p>"
          },
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body.metadata",
            "description": "<p>Input metadata from request body</p>"
          },
          {
            "group": "Success 200",
            "type": "json[]",
            "optional": false,
            "field": "body.process_chain_list",
            "description": "<p>Jobs chain list</p>"
          },
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body.progress",
            "description": "<p>Ticket progress</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "body.progress.state",
            "description": "<p>Ticket global state</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "body.progress.num_of_steps",
            "description": "<p>Number of total steps (i.e., jobs)</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "body.progress.step",
            "description": "<p>Current executing job</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success body example:",
          "content": "HTTP/1.1 200 OK\n{\n  \"_id\": \"5daf1da2a9f541a00597db3a\",\n  \"api_info\": {\n    \"method\": \"GET\",\n    \"endpoint\": \"0.0.0.0\",\n    \"path\": \"/v2/status\"\n  },\n  \"created_on\": 1571757474,\n  \"updated_on\": 1685247244,\n  \"last_access\": 1685247244,\n  \"ticket_id\": \"1571757474\",\n  \"metadata\": {},\n  \"process_chain_list\": [\n    {\n      \"job_id\": \"226bcb1d-86f6-4948-93bc-8768bd075979\",\n      \"job_code\": \"run_script_py\",\n      \"job_name\": \"ComponentReadCSV15717574740\",\n      \"job_number\": 0,\n      \"executed_on\": 1571757474.3573134,\n      \"progress\": {\n        \"state\": \"SUCCESS\",\n        \"return\": \"result\"\n      }\n    }\n  ],\n  \"progress\": {\n    \"state\": \"SUCCESS\",\n    \"num_of_steps\": 2,\n    \"step\": 2\n  }\n}",
          "type": "json"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "BadRequest",
            "description": "<p>Ticket identifier not found</p>"
          }
        ]
      }
    },
    "filename": "server/api.py",
    "groupTitle": "Ticket"
  },
  {
    "type": "post",
    "url": "/v2/run",
    "title": "Issue new ticket",
    "version": "0.1.0",
    "name": "PostTicket",
    "group": "Ticket",
    "permission": [
      {
        "name": "user"
      }
    ],
    "header": {
      "fields": {
        "Header": [
          {
            "group": "Header",
            "type": "String",
            "optional": false,
            "field": "x-api-key",
            "description": "<p>API unique access-key</p>"
          }
        ]
      }
    },
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "json",
            "optional": false,
            "field": "body",
            "description": ""
          },
          {
            "group": "Parameter",
            "type": "json",
            "optional": false,
            "field": "body.meta",
            "description": "<p>(Optional) metadata to include in the ticket's body</p>"
          },
          {
            "group": "Parameter",
            "type": "json[]",
            "optional": false,
            "field": "body.jobs",
            "description": "<p>Jobs list</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "body.jobs.task",
            "description": "<p>Job code</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "body.jobs.name",
            "description": "<p>Name/description of the job</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "body.jobs.data",
            "description": "<p>Any necessary data to run the job</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request body example:",
          "content": "{\n    meta: {},\n    jobs: [\n        {\n            \"task\":\"name_of_the_task\",\n            \"name\":\"brief description or identifier of the task\",\n            \"data\":\"required metadata to run the task\"\n        }\n    ]\n}",
          "type": "json"
        }
      ]
    },
    "examples": [
      {
        "title": "Example usage:",
        "content": "curl -X POST \\\n    http://localhost:6565/v2/run \\\n    -H 'x-api-key: CD3DC6F9EC4FCACB9A791CD7D43DD' \\\n    -d '{ \"jobs\": [{\"task\":\"run_script_py\", \"name\":\"print env\", \"data\":\"import os; print(os.environ['\\''HOME'\\''])\"}], \"meta\": {} }'",
        "type": "curl"
      }
    ],
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "json[]",
            "optional": false,
            "field": "body.api_info",
            "description": "<p>Endpoint details</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "body.ticket_id",
            "description": "<p>Unique ticket identifier</p>"
          },
          {
            "group": "Success 200",
            "type": "Date",
            "optional": false,
            "field": "body.created_on",
            "description": "<p>Ticket creation date</p>"
          },
          {
            "group": "Success 200",
            "type": "Date",
            "optional": false,
            "field": "body.updated_on",
            "description": ""
          },
          {
            "group": "Success 200",
            "type": "Date",
            "optional": false,
            "field": "body.last_access",
            "description": "<p>Last ticket's access date</p>"
          },
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body.metadata",
            "description": "<p>Input metadata from request body</p>"
          },
          {
            "group": "Success 200",
            "type": "json[]",
            "optional": false,
            "field": "body.process_chain_list",
            "description": "<p>Jobs chain list</p>"
          },
          {
            "group": "Success 200",
            "type": "json",
            "optional": false,
            "field": "body.progress",
            "description": "<p>Ticket progress</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "body.progress.state",
            "description": "<p>Ticket global state</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "body.progress.num_of_steps",
            "description": "<p>Number of total steps (i.e., jobs)</p>"
          },
          {
            "group": "Success 200",
            "type": "Integer",
            "optional": false,
            "field": "body.progress.step",
            "description": "<p>Current executing job</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success body example:",
          "content": "HTTP/1.1 200 OK\n{\n  \"_id\": \"5daf1da2a9f541a00597db3a\",\n  \"api_info\": {\n    \"method\": \"GET\",\n    \"endpoint\": \"0.0.0.0\",\n    \"path\": \"/v2/run\"\n  },\n  \"created_on\": 1571757474,\n  \"updated_on\": null,\n  \"last_access\": null,\n  \"ticket_id\": \"1571757474\",\n  \"metadata\": {},\n  \"process_chain_list\": [\n    {\n      \"job_id\": \"226bcb1d-86f6-4948-93bc-8768bd075979\",\n      \"job_code\": \"run_script_py\",\n      \"job_name\": \"ComponentReadCSV15717574740\",\n      \"job_number\": 0,\n      \"executed_on\": 1571757474.3573134,\n      \"progress\": {\n        \"state\": \"PENDING\",\n        \"return\": null\n      }\n    }\n  ],\n  \"progress\": {\n    \"state\": \"PENDING\",\n    \"num_of_steps\": 2,\n    \"step\": 0\n  }\n}",
          "type": "json"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "InternalServerError",
            "description": "<p>Input request body does not match template</p>"
          }
        ]
      }
    },
    "filename": "server/api.py",
    "groupTitle": "Ticket"
  },
  {
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "optional": false,
            "field": "varname1",
            "description": "<p>No type.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "varname2",
            "description": "<p>With type.</p>"
          }
        ]
      }
    },
    "type": "",
    "url": "",
    "version": "0.0.0",
    "filename": "server/doc/main.js",
    "group": "_home_antonio_Documents_je_platform_server_doc_main_js",
    "groupTitle": "_home_antonio_Documents_je_platform_server_doc_main_js",
    "name": ""
  }
] });
