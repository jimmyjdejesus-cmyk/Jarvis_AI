import * as assert from 'assert';
import * as sinon from 'sinon';
import { sanitizeMissionId, sanitizeBackendUrl, dagToMermaid, openDagHereCommand, Dag } from '../extension';
import type * as vscode from 'vscode';

describe('Open DAG Here Command', () => {
  it('sanitizeMissionId validates mission IDs', () => {
    assert.strictEqual(sanitizeMissionId('abc-123'), 'abc-123');
    assert.strictEqual(sanitizeMissionId('bad id!'), undefined);
  });

  it('sanitizeBackendUrl validates URLs', () => {
    assert.strictEqual(sanitizeBackendUrl('http://localhost:8000/api'), 'http://localhost:8000');
    assert.strictEqual(sanitizeBackendUrl('http://127.0.0.1:8080/'), 'http://127.0.0.1:8080');
    assert.strictEqual(sanitizeBackendUrl('https://example.com'), undefined);
    assert.strictEqual(sanitizeBackendUrl('ftp://localhost'), undefined);
    assert.strictEqual(sanitizeBackendUrl('not a url'), undefined);
  });

  it('openDagHereCommand returns early when mission ID missing', async () => {
    const windowStub = {
      activeTextEditor: { document: { fileName: 'test.ts' } },
      showInputBox: sinon.stub().resolves(undefined),
      showErrorMessage: sinon.stub(),
      createWebviewPanel: sinon.stub()
    } as unknown as typeof vscode.window;
    const workspaceStub = {
      getConfiguration: sinon.stub().returns({ get: () => 'http://localhost:8000' })
    } as unknown as typeof vscode.workspace;
    const fetchSpy = sinon.spy(async (): Promise<Dag> => ({} as Dag));
    await openDagHereCommand({ window: windowStub, workspace: workspaceStub }, fetchSpy);
    assert.strictEqual(fetchSpy.called, false);
  });

  it('openDagHereCommand rejects invalid backend URL', async () => {
    const windowStub = {
      activeTextEditor: { document: { fileName: 'test.ts' } },
      showInputBox: sinon.stub().resolves('mission1'),
      showErrorMessage: sinon.stub(),
      createWebviewPanel: sinon.stub()
    } as unknown as typeof vscode.window;
    const workspaceStub = {
      getConfiguration: sinon.stub().returns({ get: () => 'https://example.com' })
    } as unknown as typeof vscode.workspace;
    const fetchSpy = sinon.spy(async (): Promise<Dag> => ({} as Dag));
    await openDagHereCommand({ window: windowStub, workspace: workspaceStub }, fetchSpy);
    assert.strictEqual(fetchSpy.called, false);
    assert.ok((windowStub.showErrorMessage as sinon.SinonStub).called);
  });

  it('dagToMermaid omits highlight when file not in DAG', () => {
    const dag: Dag = { nodes: { a: { capability: 'C1', state: { provenance: { path: 'other.ts' } } } }, edges: [] };
    const result = dagToMermaid(dag, 'test.ts');
    assert.ok(!result.includes('style'));
  });
});
