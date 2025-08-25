"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.openDagHereCommand = exports.sanitizeBackendUrl = exports.sanitizeMissionId = exports.dagToMermaid = exports.fetchDag = exports.activate = void 0;
const http = __importStar(require("http"));
let vscode;
try {
    // `vscode` is only available inside VS Code; fall back to an empty object for tests.
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    vscode = require('vscode');
}
catch (_a) {
    vscode = {};
}
/**
 * Activate extension and register all Jarvis commands.
 */
function activate(context) {
    const planMission = vscode.commands.registerCommand('jarvis.planMission', () => __awaiter(this, void 0, void 0, function* () {
        vscode.window.showInformationMessage('Plan Mission is not implemented yet.');
    }));
    const runStep = vscode.commands.registerCommand('jarvis.runStep', () => __awaiter(this, void 0, void 0, function* () {
        vscode.window.showInformationMessage('Run Step is not implemented yet.');
    }));
    const approveHitl = vscode.commands.registerCommand('jarvis.approveHitl', () => __awaiter(this, void 0, void 0, function* () {
        vscode.window.showInformationMessage('Approve HITL is not implemented yet.');
    }));
    const openDagHere = vscode.commands.registerCommand('jarvis.openDagHere', () => openDagHereCommand());
    context.subscriptions.push(planMission, runStep, approveHitl, openDagHere);
}
exports.activate = activate;
/**
 * Request the mission DAG from the backend service.
 * @param missionId sanitized mission identifier
 * @param backendUrl base URL for the backend service
 */
function fetchDag(missionId, backendUrl) {
    return __awaiter(this, void 0, void 0, function* () {
        const url = `${backendUrl.replace(/\/$/, '')}/api/workflow/${missionId}`;
        return new Promise((resolve, reject) => {
            http.get(url, res => {
                const { statusCode } = res;
                if (statusCode !== 200) {
                    reject(new Error(`Request Failed. Status: ${statusCode}`));
                    res.resume();
                    return;
                }
                let rawData = '';
                res.setEncoding('utf8');
                res.on('data', chunk => rawData += chunk);
                res.on('end', () => {
                    try {
                        const parsed = JSON.parse(rawData);
                        resolve(parsed);
                    }
                    catch (e) {
                        reject(e);
                    }
                });
            }).on('error', reject);
        });
    });
}
exports.fetchDag = fetchDag;
/**
 * Convert a DAG description into Mermaid graph syntax highlighting nodes
 * associated with the provided file path.
 */
function dagToMermaid(dag, filePath) {
    const nodes = dag.nodes || {};
    const edges = dag.edges || [];
    let graph = 'graph TD\n';
    const highlight = [];
    for (const [id, node] of Object.entries(nodes)) {
        graph += `${id}["${node.capability}"]\n`;
        const provenance = node.state && node.state.provenance;
        if (provenance && provenance.path === filePath) {
            highlight.push(id);
        }
    }
    for (const [from, to] of edges) {
        graph += `${from}-->${to}\n`;
    }
    for (const id of highlight) {
        graph += `style ${id} fill:#f9f,stroke:#333,stroke-width:4px\n`;
    }
    return graph;
}
exports.dagToMermaid = dagToMermaid;
/**
 * Sanitize user-provided mission identifier.
 */
function sanitizeMissionId(input) {
    if (!input) {
        return undefined;
    }
    const trimmed = input.trim();
    return /^[\w-]+$/.test(trimmed) ? trimmed : undefined;
}
exports.sanitizeMissionId = sanitizeMissionId;
/**
 * Validate and sanitize backend URL configuration.
 * Accepts only HTTP(S) URLs targeting localhost and returns the origin without
 * trailing slash.
 */
function sanitizeBackendUrl(input) {
    if (!input) {
        return undefined;
    }
    try {
        const url = new URL(input);
        if (url.protocol !== 'http:' && url.protocol !== 'https:') {
            return undefined;
        }
        const allowedHosts = ['localhost', '127.0.0.1', '[::1]'];
        if (!allowedHosts.includes(url.hostname)) {
            return undefined;
        }
        return url.origin;
    }
    catch (_a) {
        return undefined;
    }
}
exports.sanitizeBackendUrl = sanitizeBackendUrl;
/**
 * Handler for the "Open DAG Here" command.
 * Resolves the mission ID from user input, fetches the corresponding DAG,
 * highlights the node touching the active file, and renders it in a webview.
 */
function openDagHereCommand(api = { window: vscode.window, workspace: vscode.workspace }, fetchFn = fetchDag) {
    return __awaiter(this, void 0, void 0, function* () {
        const editor = api.window.activeTextEditor;
        if (!editor) {
            api.window.showErrorMessage('No active editor');
            return;
        }
        const filePath = editor.document.fileName;
        const input = yield api.window.showInputBox({ prompt: 'Mission ID', ignoreFocusOut: true });
        const missionId = sanitizeMissionId(input);
        if (!missionId) {
            return;
        }
        try {
            const config = api.workspace.getConfiguration('jarvis');
            const backendUrlConfig = config.get('backendUrl', 'http://localhost:8000');
            const backendUrl = sanitizeBackendUrl(backendUrlConfig);
            if (!backendUrl) {
                api.window.showErrorMessage('Invalid backend URL');
                return;
            }
            const dag = yield fetchFn(missionId, backendUrl);
            const mermaid = dagToMermaid(dag, filePath);
            const panel = api.window.createWebviewPanel('jarvisDag', `Mission ${missionId} DAG`, vscode.ViewColumn.Beside, { enableScripts: true });
            panel.webview.html = getWebviewContent(mermaid);
        }
        catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            api.window.showErrorMessage(`Failed to open DAG: ${message}`);
        }
    });
}
exports.openDagHereCommand = openDagHereCommand;
function getWebviewContent(mermaid) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
<div class="mermaid">
${mermaid}
</div>
<script>mermaid.initialize({startOnLoad:true});</script>
</body>
</html>`;
}
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map