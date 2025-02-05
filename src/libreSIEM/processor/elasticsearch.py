"""Elasticsearch management for LibreSIEM."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from elasticsearch import Elasticsearch
from libreSIEM.config import Settings, get_settings

logger = logging.getLogger(__name__)

class ElasticsearchManager:
    """Manages Elasticsearch indices and templates for LibreSIEM."""
    
    def __init__(self, settings: Settings = None):
        self.settings = settings or get_settings()
        
        # Initialize Elasticsearch client
        self.es = Elasticsearch(
            hosts=[self.settings.elasticsearch.ES_HOSTS],
            basic_auth=(self.settings.elasticsearch.ES_USERNAME, self.settings.elasticsearch.ES_PASSWORD)
            if self.settings.elasticsearch.ES_USERNAME and self.settings.elasticsearch.ES_PASSWORD
            else None,
            verify_certs=self.settings.elasticsearch.ES_SSL_VERIFY
        )
        
        # Initialize indices and templates
        self._setup_index_template()
        self._setup_ilm_policy()
        self._ensure_current_index()
    
    def _setup_index_template(self):
        """Set up the index template for logs."""
        template_name = "libresiem-logs"
        template_body = {
            "index_patterns": ["logs-*"],
            "template": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1,
                    "index.lifecycle.name": "libresiem-logs",
                    "index.lifecycle.rollover_alias": "logs-write"
                },
                "mappings": {
                    "properties": {
                        "timestamp": {"type": "date"},
                        "source": {"type": "keyword"},
                        "event_type": {"type": "keyword"},
                        "vendor": {"type": "keyword"},
                        "data": {
                            "type": "object",
                            "dynamic": True
                        },
                        "enriched": {
                            "type": "object",
                            "properties": {
                                "processing_timestamp": {"type": "date"},
                                "ip_info": {
                                    "type": "object",
                                    "properties": {
                                        "country": {"type": "keyword"},
                                        "city": {"type": "keyword"},
                                        "asn": {"type": "keyword"},
                                        "is_known_bad": {"type": "boolean"}
                                    }
                                },
                                "threat_intel": {
                                    "type": "object",
                                    "properties": {
                                        "score": {"type": "float"},
                                        "categories": {"type": "keyword"},
                                        "last_seen": {"type": "date"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        try:
            self.es.indices.put_index_template(name=template_name, body=template_body)
            logger.info(f"Successfully created/updated index template '{template_name}'")
        except Exception as e:
            logger.error(f"Error creating index template: {e}")
            raise
    
    def _setup_ilm_policy(self):
        """Set up the Index Lifecycle Management policy."""
        policy_name = "libresiem-logs"
        policy_body = {
            "policy": {
                "phases": {
                    "hot": {
                        "min_age": "0ms",
                        "actions": {
                            "rollover": {
                                "max_age": "30d",
                                "max_size": "50gb"
                            },
                            "set_priority": {
                                "priority": 100
                            }
                        }
                    },
                    "warm": {
                        "min_age": "30d",
                        "actions": {
                            "shrink": {
                                "number_of_shards": 1
                            },
                            "forcemerge": {
                                "max_num_segments": 1
                            },
                            "set_priority": {
                                "priority": 50
                            }
                        }
                    },
                    "cold": {
                        "min_age": "90d",
                        "actions": {
                            "set_priority": {
                                "priority": 0
                            }
                        }
                    },
                    "delete": {
                        "min_age": "365d",
                        "actions": {
                            "delete": {}
                        }
                    }
                }
            }
        }
        
        try:
            self.es.ilm.put_lifecycle(name=policy_name, policy=policy_body)
            logger.info(f"Successfully created/updated ILM policy '{policy_name}'")
        except Exception as e:
            logger.error(f"Error creating ILM policy: {e}")
            raise
    
    def _ensure_current_index(self):
        """Ensure the current month's index exists."""
        current_index = f"logs-{datetime.now().strftime('%Y.%m')}"
        alias_name = "logs-write"
        
        try:
            # Check if the write alias exists
            alias_exists = self.es.indices.exists_alias(name=alias_name)
            if not alias_exists:
                # Create the initial index and alias
                self.es.indices.create(
                    index=current_index,
                    body={
                        "aliases": {
                            alias_name: {
                                "is_write_index": True
                            }
                        }
                    }
                )
                logger.info(f"Created initial index {current_index} with write alias {alias_name}")
            else:
                # Ensure the current index exists in case we need to roll over
                if not self.es.indices.exists(index=current_index):
                    self.es.indices.rollover(alias=alias_name)
                    logger.info(f"Rolled over to new index {current_index}")
        except Exception as e:
            logger.error(f"Error ensuring current index: {e}")
            raise
    
    def store_document(self, doc: Dict[str, Any]):
        """Store a document in the current index."""
        try:
            self.es.index(
                index="logs-write",
                document=doc,
                pipeline="logs_enrichment"
            )
        except Exception as e:
            logger.error(f"Error storing document: {e}")
            raise
    
    def search_logs(
        self,
        query: Dict[str, Any],
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        size: int = 100,
        from_: int = 0
    ) -> Dict[str, Any]:
        """Search logs with optional time range."""
        search_body = {"query": query}
        
        # Add time range if specified
        if start_time or end_time:
            search_body["query"] = {
                "bool": {
                    "must": [query],
                    "filter": [{
                        "range": {
                            "timestamp": {
                                **({"gte": start_time.isoformat()} if start_time else {}),
                                **({"lte": end_time.isoformat()} if end_time else {})
                            }
                        }
                    }]
                }
            }
        
        try:
            return self.es.search(
                index="logs-*",
                body=search_body,
                size=size,
                from_=from_
            )
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            raise
