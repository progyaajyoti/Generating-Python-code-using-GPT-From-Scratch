from tokenizers import ByteLevelBPETokenizer
from transformers import GPT2Config, GPT2LMHeadModel, GPT2Tokenizer, DataCollatorForLanguageModeling
from datasets import load_dataset
from transformers import Trainer, TrainingArguments

TRAIN_BASE = True

if TRAIN_BASE:
    paths = ["python_code_text_data.txt"]

    tokenizer = ByteLevelBPETokenizer()

    tokenizer.train(files=paths, vocab_size=52_000, min_frequency=2, special_tokens=[
        "<s>",
        "<pad>",
        "</s>",
        "<unk>",
        "<mask>"
    ])

    # Save files to disk
    tokenizer.save_model("tokenizer")

# Ensure that the tokenizer is saved and can be loaded correctly
tokenizer = GPT2Tokenizer.from_pretrained('./tokenizer')

tokenizer.add_special_tokens({
    "eos_token": "</s>",
    "bos_token": "<s>",
    "unk_token": "<unk>",
    "pad_token": "<pad>",
    "mask_token": "<mask>"
})

inp = "print('Hello world!')"
t = tokenizer.encode(inp)
print(t)
print(tokenizer.decode(t))


config = GPT2Config(
    vocab_size = tokenizer.vocab_size,
    bos_token = tokenizer.bos_token_id,
    eos_token = tokenizer.eos_token_id
)


model = GPT2LMHeadModel(config)

dataset = load_dataset("text", data_files=paths)

def encode(lines):
    return tokenizer(lines['text'], add_special_tokens=True, truncation=True, max_length=512)

dataset.set_transform(encode)
dataset = dataset['train']

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=True, mlm_probability=0.15)


training_args = TrainingArguments (
        output_dir="GPyT",
        overwrite_output_dir= True, 
        num_train_epochs=1,
        per_device_train_batch_size=10, 
        save_steps=100, 
        save_total_limit=2, 
        prediction_loss_only=True,
        remove_unused_columns =False
)
trainer = Trainer (
        model=model, 
        args=training_args, 
        data_collator=data_collator,
        train_dataset=dataset,
)

trainer.train()

trainer.save_model("GPyT")