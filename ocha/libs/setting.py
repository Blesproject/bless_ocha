database_setting = {
    "driver": {
        "mysql": {
            "constructor": "__init__.py.mysql",
            "package": {
                "name": "pymysql",
                "tools": "pip"
            }
        },
        "cockroachdb": {
            "constructor": "__init__.py.cockroachdb",
            "package": {
                "name": "psycopg2",
                "tools": "pip"
            }
        },
        "mariadb": {
            "constructor": "__init__.py.mysql",
            "package": {
                "name": "pymysql",
                "tools": "pip"
            }
        },
        "postgresql": {
            "constructor": "__init__.py.postgresql",
            "package": {
                "name": "psycopg2",
                "tools": "pip"
            }
        },
        "mongodb": {
            "constructor": "__init__.py.mongo",
            "package": {
                "name": "flaskmongoengine",
                "tools": "pip"
            }
        }
    }
}

framework_setting = {
    "flask": {
      "default": {
        "url": "https://",
        "package": {
          "name": "psycopg2",
          "tools": "pip"
        }
      },
      "mysql": {
        "url": "https://",
        "package": {
          "name": "pymysql",
          "tools": "pip"
        }
      },
      "mongodb": {
        "url": "https://",
        "package": {
          "name": "mongoengine",
          "tools": "pip"
        }
      }
    }
  }

default_table = {
  "tb_userdata": {
    "id_userdata": {
      "type": "serial",
      "notNull": True,
      "primaryKey": True
    },
    "first_name": {
      "type": "varchar",
      "notNull": True
    },
    "last_name": {
      "type": "varchar",
      "notNull": True
    },
    "location": {
      "type": "varchar"
    },
    "email": {
      "type": "varchar",
      "unique": True
    }
  },
  "tb_user": {
    "id_user": {
      "type": "serial",
      "notNull": True,
      "primaryKey": True
    },
    "id_userdata": {
      "type": "int",
      "notNull": True,
      "foreignKey": {
        "reference": "tb_userdata",
        "field": "id_userdata",
        "on_delete": "cascade",
        "on_update": "cascade"
      }
    },
    "username": {
      "type": "varchar",
      "unique": True
    },
    "password": {
      "type": "varchar"
    }
  }
}