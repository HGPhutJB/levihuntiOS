import UIKit
import WebKit

final class ViewController: UIViewController, WKNavigationDelegate, WKUIDelegate {

    private var webView: WKWebView!
    private let bgColor = UIColor(red: 0.769, green: 0.882, blue: 1.0, alpha: 1.0)

    override var preferredStatusBarStyle: UIStatusBarStyle { return .default }

    // iPhone: chỉ dọc. iPad: xoay tự do.
    override var supportedInterfaceOrientations: UIInterfaceOrientationMask {
        return UIDevice.current.userInterfaceIdiom == .phone ? .portrait : .all
    }

    override func loadView() {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        let wv = WKWebView(frame: UIScreen.main.bounds, configuration: config)
        wv.navigationDelegate = self
        wv.uiDelegate = self
        wv.scrollView.contentInsetAdjustmentBehavior = .never   // toàn màn hình, trang tự xử lý safe-area
        wv.scrollView.bounces = false
        wv.isOpaque = false
        wv.backgroundColor = bgColor
        wv.scrollView.backgroundColor = bgColor
        webView = wv
        view = wv
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        loadApp()
    }

    private func loadApp() {
        guard let www = Bundle.main.url(forResource: "www", withExtension: nil) else { return }
        webView.loadFileURL(www.appendingPathComponent("index.html"), allowingReadAccessTo: www)
    }

    private func openExternally(_ url: URL) {
        UIApplication.shared.open(url, options: [:], completionHandler: nil)
    }

    // Link ra ngoài (Discord, Roblox, YouTube, https...) -> mở bằng Safari / app tương ứng
    func webView(_ webView: WKWebView,
                 decidePolicyFor navigationAction: WKNavigationAction,
                 decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        guard let url = navigationAction.request.url, let scheme = url.scheme?.lowercased() else {
            decisionHandler(.allow); return
        }
        let internalSchemes: Set<String> = ["file", "about", "blob", "data"]
        let isMainFrameOrNewWindow = navigationAction.targetFrame?.isMainFrame ?? true
        if !internalSchemes.contains(scheme) && isMainFrameOrNewWindow {
            openExternally(url)
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }

    // target="_blank"
    func webView(_ webView: WKWebView,
                 createWebViewWith configuration: WKWebViewConfiguration,
                 for navigationAction: WKNavigationAction,
                 windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = navigationAction.request.url { openExternally(url) }
        return nil
    }

    func webViewWebContentProcessDidTerminate(_ webView: WKWebView) {
        loadApp()
    }

    // alert / confirm / prompt của JavaScript
    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let a = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "OK", style: .default) { _ in completionHandler() })
        present(a, animated: true)
    }

    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String,
                 initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        let a = UIAlertController(title: nil, message: message, preferredStyle: .alert)
        a.addAction(UIAlertAction(title: "Hủy", style: .cancel) { _ in completionHandler(false) })
        a.addAction(UIAlertAction(title: "OK", style: .default) { _ in completionHandler(true) })
        present(a, animated: true)
    }
}
