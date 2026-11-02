import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import Generator from './Generator.svelte';

const API = 'https://api.example.test';

/** The highlighted snippet as plain text. */
const snippet = () => document.querySelector('pre')?.textContent ?? '';
const preview = () => document.querySelector<HTMLImageElement>('.stage img');

let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  // Title lookups (noembed) answer with nothing unless a test says otherwise
  fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 200 }));
  vi.stubGlobal('fetch', fetchMock);
  history.replaceState(null, '', '/');
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('Generator', () => {
  it('starts with an empty preview and a template snippet', () => {
    render(Generator);
    expect(screen.getByText('Your thumbnail will appear here')).toBeInTheDocument();
    expect(preview()).toBeNull();
    expect(snippet()).toContain('VIDEO_ID');
  });

  // The scenario from #113: a valid YouTube URL and a title give an image and code
  it('shows the thumbnail and the embed code for a YouTube link and title', async () => {
    const user = userEvent.setup();
    render(Generator);

    await user.type(screen.getByLabelText('Video URL'), 'https://youtu.be/dQw4w9WgXcQ');
    await user.type(screen.getByLabelText(/Title/), 'Never gonna give you up');

    const img = preview()!;
    expect(img).not.toBeNull();
    expect(img.getAttribute('src')).toBe(`${API}/youtube/dQw4w9WgXcQ`);
    expect(img).toHaveAttribute('alt', 'Never gonna give you up');
    expect(img.closest('a')).toHaveAttribute('href', 'https://youtu.be/dQw4w9WgXcQ');

    // Loading state until the image arrives
    expect(screen.getByText('Generating thumbnail…')).toBeInTheDocument();
    await fireEvent.load(img);
    expect(img).toHaveClass('ready');
    expect(screen.queryByText('Generating thumbnail…')).toBeNull();

    expect(snippet()).toBe(`[![Never gonna give you up](${API}/youtube/dQw4w9WgXcQ)](https://youtu.be/dQw4w9WgXcQ)`);
    expect(screen.getByText('YouTube')).toBeInTheDocument();
  });

  it('switches between Markdown, HTML and image URL output', async () => {
    const user = userEvent.setup();
    render(Generator);
    await user.type(screen.getByLabelText('Video URL'), 'https://youtu.be/dQw4w9WgXcQ');

    await user.click(screen.getByRole('tab', { name: 'HTML' }));
    expect(snippet()).toContain('<a href="https://youtu.be/dQw4w9WgXcQ">');
    expect(snippet()).toContain('width="320" height="180"');

    await user.click(screen.getByRole('tab', { name: 'Image URL' }));
    expect(snippet()).toBe(`${API}/youtube/dQw4w9WgXcQ`);
  });

  it('copies the current snippet to the clipboard', async () => {
    const user = userEvent.setup();
    render(Generator);
    await user.type(screen.getByLabelText('Video URL'), 'https://youtu.be/dQw4w9WgXcQ');

    await user.click(screen.getByRole('button', { name: /Copy Markdown/ }));
    expect(await navigator.clipboard.readText()).toBe(snippet());
    expect(screen.getByText('Copied!')).toBeInTheDocument();
  });

  it('explains when a link is not a YouTube or Vimeo video', async () => {
    const user = userEvent.setup();
    render(Generator);
    await user.type(screen.getByLabelText('Video URL'), 'https://example.com/video');

    expect(screen.getByText(/isn’t a link we support yet \(YouTube, Vimeo, Imgur, Loom, Dailymotion, Streamable, Rumble, Instagram or Facebook\)/)).toBeInTheDocument();
    expect(screen.getByLabelText('Video URL')).toHaveAttribute('aria-invalid', 'true');
    expect(preview()).toBeNull();
  });

  it('only offers animated GIFs for YouTube', async () => {
    const user = userEvent.setup();
    render(Generator);
    const gif = screen.getByRole('radio', { name: 'Animated GIF' });

    await user.type(screen.getByLabelText('Video URL'), 'https://vimeo.com/76979871');
    expect(gif).toBeDisabled();

    await user.clear(screen.getByLabelText('Video URL'));
    await user.type(screen.getByLabelText('Video URL'), 'https://i.imgur.com/A61SaA1.mp4');
    expect(gif).toBeDisabled();

    await user.clear(screen.getByLabelText('Video URL'));
    await user.type(screen.getByLabelText('Video URL'), 'https://youtu.be/dQw4w9WgXcQ');
    expect(gif).toBeEnabled();
    await user.click(gif);
    expect(snippet()).toContain(`${API}/youtube/dQw4w9WgXcQ.gif`);
  });

  it('updates the code at once but waits before reloading the preview', async () => {
    const user = userEvent.setup();
    render(Generator);
    await user.type(screen.getByLabelText('Video URL'), 'https://youtu.be/dQw4w9WgXcQ');

    await user.click(screen.getByRole('radio', { name: 'L' }));
    expect(snippet()).toContain('?width=640&height=360');
    expect(preview()!.getAttribute('src')).toBe(`${API}/youtube/dQw4w9WgXcQ`);
    await waitFor(() => expect(preview()!.getAttribute('src')).toBe(`${API}/youtube/dQw4w9WgXcQ?width=640&height=360`));
  });

  it('shows the error from the API when a thumbnail cannot be made', async () => {
    fetchMock.mockImplementation(async (url: string) =>
      url.startsWith(`${API}/url`)
        ? new Response(JSON.stringify({ detail: 'That video does not exist.' }), { status: 400 })
        : new Response('{}')
    );
    const user = userEvent.setup();
    render(Generator);
    await user.type(screen.getByLabelText('Video URL'), 'https://youtu.be/dQw4w9WgXcQ');

    await fireEvent.error(preview()!);
    // A generic message shows at once, then the API's own explanation replaces it
    const alert = await screen.findByRole('alert');
    await waitFor(() => expect(alert).toHaveTextContent('That video does not exist.'));
  });

  it("fills in the video's title unless the user wrote one", async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ title: 'Rick Astley - Never Gonna Give You Up' })));
    const user = userEvent.setup();
    render(Generator);
    await user.type(screen.getByLabelText('Video URL'), 'https://youtu.be/dQw4w9WgXcQ');

    await waitFor(() => expect(screen.getByLabelText(/Title/)).toHaveValue('Rick Astley - Never Gonna Give You Up'));
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('noembed.com/embed?url=https%3A%2F%2Fyoutu.be%2FdQw4w9WgXcQ'),
      expect.anything()
    );
  });

  it('fills in the example title for the rickroll example', async () => {
    const user = userEvent.setup();
    render(Generator);
    await user.click(screen.getByRole('button', { name: 'youtu.be link' }));

    expect(screen.getByLabelText('Video URL')).toHaveValue('https://youtu.be/dQw4w9WgXcQ');
    expect(screen.getByLabelText(/Title/)).toHaveValue('Definitely not a rickroll');
  });

  it('reads and writes the ?video= query parameter', async () => {
    history.replaceState(null, '', '/?video=https%3A%2F%2Fvimeo.com%2F76979871');
    const user = userEvent.setup();
    render(Generator);

    await waitFor(() => expect(screen.getByLabelText('Video URL')).toHaveValue('https://vimeo.com/76979871'));
    expect(snippet()).toContain(`${API}/vimeo/76979871`);

    await user.clear(screen.getByLabelText('Video URL'));
    expect(location.search).toBe('');
  });
});
