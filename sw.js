// MyBiz News service worker
const CACHE = "mybiz-news-v2";
const SHELL = ["./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener("fetch", e => {
  const req = e.request;
  const url = new URL(req.url);
  const isHTML = req.mode === "navigate" || url.pathname.endsWith("/") || url.pathname.endsWith("index.html");
  const isData = url.pathname.endsWith("articles.json");

  // アプリ本体(HTML)とデータ = ネット優先（最新を取りにいく／オフラインはキャッシュ）
  if (isHTML || isData) {
    e.respondWith(
      fetch(req).then(r => { const cp = r.clone(); caches.open(CACHE).then(c => c.put(req, cp)); return r; })
                .catch(() => caches.match(req).then(m => m || caches.match("./index.html")))
    );
    return;
  }
  // それ以外(アイコン等) = キャッシュ優先
  e.respondWith(caches.match(req).then(r => r || fetch(req)));
});
