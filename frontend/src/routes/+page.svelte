<script lang="ts">
    let input_types = [
		{ id: 1, text: `url`, placeholder: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`, placeholder_title: `rick-roll`},
		{ id: 2, text: `id`, placeholder: `dQw4w9WgXcQ`, placeholder_title: `rick-roll`}
    ]

    let selected;

	function handleSubmit() {
		alert(`answered question ${selected.id} (${selected.text}) with "${answer}"`);
	}
</script>

<section class="center-section">
    <div class="titles">
        <h1>Welcome <br/>
            to  <br/>
            Markdown Videos!</h1>
        <h2>add beautiful video thumbnails to your markdown content</h2>
    </div>
    <div class="center vertical-flex-container">
        <form class="center" on:submit|preventDefault={handleSubmit}>
            <div class="inputs-container vertical-flex-container">
                <div class="vertical-flex-container">
                    <label for="api-input-field">{selected?.text ?? "url"}</label>
                    <select bind:value={selected}>
                        {#each input_types as type}
                            <option value={type}>
                                {type.text}
                            </option>
                        {/each}
                    </select>
                    <input name="input-url" placeholder="{selected?.placeholder}"/>
                </div>
                <div class="vertical-flex-container">
                    <label for="api-input-field">title</label>
                    <input name="input-title" placeholder="{selected?.placeholder_title}"/>
                </div>
            </div>
            <button class="btn-generate-markdown">Generate Markdown</button>
        </form>
        <div class="preview-image center"></div>
    </div>
</section>

<style lang="scss">
    h1 {
        font-size: 4rem;
        margin-bottom: 0;
    }
    h2 {
        font-size: 20px;
        margin-bottom: 5rem;
        font-family: 'Courier New', Courier, monospace;
        color: silver;
    }
    label {
        text-transform: uppercase;
        font-family:Cambria, Cochin, Georgia, Times, 'Times New Roman', serif
    }
    .center-section {
        text-align: center;
        padding-bottom: 5rem;
        padding-top: 2rem;
        margin: 1rem;
        background-color: #353535;
        color: mintcream;
        font-family: 'Gill Sans', 'Gill Sans MT', Calibri, 'Trebuchet MS', sans-serif
    }
    .center {
        display:inline-block;
    }
    .vertical-flex-container {
        display: flex;
        flex-wrap: nowrap;
        flex-direction: column;
    }
    .inputs-container > * {
        margin-top: 1rem;
        display: inline-block;
    }
    .btn-generate-markdown {
        padding: .25rem;
        margin-top: 1rem;
    }
    .preview-image {
        height: 180px;
        width: 320px;
        margin-top: 1rem;
        background-color: #222222;
        margin: 1rem auto;
    }
</style>