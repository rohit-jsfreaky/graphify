| row | django R@10 / hit@10 | flask R@10 / hit@10 | requests R@10 / hit@10 | hono R@10 / hit@10 | jsoup R@10 / hit@10 | caddy R@10 / hit@10 | ALL R@5 | ALL R@10 | ALL R@20 | ALL hit@10 | ALL P@10 or shown@10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| v8 `affected` (graph items only) | 0.114 / 0.250 | 0.058 / 0.161 | 0.365 / 0.681 | 0.318 / 0.414 | 0.117 / 0.337 | 0.103 / 0.197 | 0.137 | 0.179 | 0.221 | 0.340 | 0.078 |
| built: co-change section, then code links (shipped order) | 0.322 / 0.566 | 0.415 / 0.677 | 0.519 / 0.830 | 0.698 / 0.888 | 0.514 / 0.902 | 0.422 / 0.626 | 0.399 | 0.482 | 0.510 | 0.748 | 0.155 |
| first build's layout: code links, then section | 0.264 / 0.491 | 0.271 / 0.452 | 0.395 / 0.723 | 0.663 / 0.844 | 0.410 / 0.801 | 0.235 / 0.359 | 0.285 | 0.373 | 0.454 | 0.612 | 0.126 |
| built, first k graph files + whole co-change section | 0.327 / 0.570 | 0.422 / 0.677 | 0.536 / 0.830 | 0.710 / 0.892 | 0.538 / 0.906 | 0.426 / 0.628 | 0.469 | 0.493 | 0.518 | 0.750 | 8.411 |

Queries per repo: django 760, flask 31, requests 47, hono 473, jsoup 297, caddy 462
Unresolved seeds (CLI would exit 4): django 0, flask 0, requests 0, hono 6, jsoup 0, caddy 0
