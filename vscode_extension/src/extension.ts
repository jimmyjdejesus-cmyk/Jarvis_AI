import * as http from 'http';
import type * as vscodeTypes from 'vscode';

let vscode: typeof vscodeTypes;
try {
    // `vscode` is only available inside VS Code; fall back to an empty object for tests.
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    vscode = require('vscode');
} catch {
    vscode = {} as unknown as typeof vscodeTypes;
}

interface DagNode {
    capability: string;
    state?: { provenance?: { path?: string } };
}

export interface Dag {
    nodes?: Record<string, DagNode>;
    edges?: [string, string][];
}

/**
 * Activate extension and register all Jarvis commands.
 */
export function activate(context: vscodeTypes.ExtensionContext) {
    const planMission = vscode.commands.registerCommand('jarvis.planMission', async () => {
        vscode.window.showInformationMessage('Plan Mission is not implemented yet.');
    });

    const runStep = vscode.commands.registerCommand('jarvis.runStep', async () => {
        vscode.window.showInformationMessage('Run Step is not implemented yet.');
    });

    const approveHitl = vscode.commands.registerCommand('jarvis.approveHitl', async () => {
        vscode.window.showInformationMessage('Approve HITL is not implemented yet.');
    });

    const openDagHere = vscode.commands.registerCommand('jarvis.openDagHere', () => openDagHereCommand());

    context.subscriptions.push(planMission, runStep, approveHitl, openDagHere);
}

/**
 * Request the mission DAG from the backend service.
 * @param missionId sanitized mission identifier
 * @param backendUrl base URL for the backend service
 */
export async function fetchDag(missionId: string, backendUrl: string): Promise<Dag> {
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
                    const parsed = JSON.parse(rawData) as Dag;
                    resolve(parsed);
                } catch (e) {
                    reject(e);
                }
            });
        }).on('error', reject);
    });
}

/**
 * Convert a DAG description into Mermaid graph syntax highlighting nodes
 * associated with the provided file path.
 */
export function dagToMermaid(dag: Dag, filePath: string): string {
    const nodes: Record<string, DagNode> = dag.nodes || {};
    const edges: [string, string][] = dag.edges || [];
    let graph = 'graph TD\n';
    const highlight: string[] = [];

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

/**
 * Sanitize user-provided mission identifier.
 */
export function sanitizeMissionId(input?: string): string | undefined {
    if (!input) {
        return undefined;
    }
    const trimmed = input.trim();
    return /^[\w-]+$/.test(trimmed) ? trimmed : undefined;
}

/**
 * Validate and sanitize backend URL configuration.
 * Accepts only HTTP(S) URLs targeting localhost and returns the origin without
 * trailing slash.
 */
export function sanitizeBackendUrl(input?: string): string | undefined {
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
    } catch {
        return undefined;
    }
}

/**
 * Handler for the "Open DAG Here" command.
 * Resolves the mission ID from user input, fetches the corresponding DAG,
 * highlights the node touching the active file, and renders it in a webview.
 */
export async function openDagHereCommand(
    api: { window: typeof vscodeTypes.window; workspace: typeof vscodeTypes.workspace } = { window: vscode.window, workspace: vscode.workspace },
    fetchFn: typeof fetchDag = fetchDag
): Promise<void> {
    const editor = api.window.activeTextEditor;
    if (!editor) {
        api.window.showErrorMessage('No active editor');
        return;
    }
    const filePath = editor.document.fileName;
    const input = await api.window.showInputBox({ prompt: 'Mission ID', ignoreFocusOut: true });
    const missionId = sanitizeMissionId(input);
    if (!missionId) {
        return;
    }
    try {
        const config = api.workspace.getConfiguration('jarvis');
        const backendUrlConfig = config.get<string>('backendUrl', 'http://localhost:8000');
        const backendUrl = sanitizeBackendUrl(backendUrlConfig);
        if (!backendUrl) {
            api.window.showErrorMessage('Invalid backend URL');
            return;
        }
        const dag = await fetchFn(missionId, backendUrl);
        const mermaid = dagToMermaid(dag, filePath);
        const panel = api.window.createWebviewPanel('jarvisDag', `Mission ${missionId} DAG`, vscode.ViewColumn.Beside, { enableScripts: true });
        panel.webview.html = getWebviewContent(mermaid);
    } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        api.window.showErrorMessage(`Failed to open DAG: ${message}`);
    }
}

function getWebviewContent(mermaid: string): string {
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

export function deactivate() {}
