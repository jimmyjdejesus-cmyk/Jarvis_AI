import * as vscode from 'vscode';
import { JarvisClient } from './websocketClient';

let client: JarvisClient;

export async function activate(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration('jarvis');
  const url = config.get<string>('serverUrl') || 'ws://localhost:8765';
  client = new JarvisClient(url);
  try {
    await client.connect();
  } catch (err) {
    vscode.window.showErrorMessage(`Jarvis connection failed: ${err}`);
  }

  context.subscriptions.push(
    vscode.languages.registerInlineCompletionItemProvider({ pattern: '**' }, {
      async provideInlineCompletionItems(document, position) {
        const line = document.lineAt(position.line);
        const prefix = line.text.substring(0, position.character);
        const res = await client.sendRequest({
          command: 'inline-suggestion',
          code: prefix,
          language: document.languageId
        });
        const text: string | undefined = res?.suggestion || res?.explanation;
        if (text) {
          const range = new vscode.Range(position, position);
          const item = new vscode.InlineCompletionItem(text);
          item.range = range;
          return [item];
        }
        return [];
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('jarvis.streamContext', async () => {
      const folders = vscode.workspace.workspaceFolders;
      if (!folders || folders.length === 0) {
        vscode.window.showInformationMessage('No workspace opened');
        return;
      }
      await client.sendRequest({
        command: 'stream-context',
        workspace: folders[0].uri.fsPath
      });
      vscode.window.showInformationMessage('Repository context streamed to Jarvis');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('jarvis.debugError', async () => {
      const error = await vscode.window.showInputBox({ prompt: 'Error message' });
      if (!error) {
        return;
      }
      const editor = vscode.window.activeTextEditor;
      const code = editor?.document.getText() || '';
      const language = editor?.document.languageId || 'plaintext';
      const res = await client.sendRequest({
        command: 'debug-error',
        error,
        code,
        language
      });
      if (res && res.debug_help) {
        vscode.window.showInformationMessage(res.debug_help);
      }
    })
  );
}

export function deactivate() {
  client?.dispose();
}
