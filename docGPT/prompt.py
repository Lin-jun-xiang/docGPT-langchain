from abc import ABC, abstractmethod

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate


class Promptor(ABC):
    @abstractmethod
    def get_schemas(self):
        pass

    @abstractmethod
    def get_prompt(self):
        pass


class SpecificationPromptor(Promptor):
    """
    1. Design a prompt template for a businese algorithm
    2. Extract the specification of product
    """

    prompt_template = """
    Use the following pieces of context to answer the question, if you don't know the answer, leave it blank('') don't try to make up an answer.

    {context}

    Question: {question}
    The specifications including: product_name, manufactured_date, size_inch, resolution, contrast, operation_temperature, power_supply
    And the following specifications keys are expected to be expressed as True/False: sunlight_readable, antiglare, low power/consumption (power saving), high brightness, wide temperature, fast response

    Answer in JSON representations
    """

    @property
    def get_schemas(self):
        SCHEMAS = {
            'name': [
                'company_name', 'product_name', 'manufactured_date',
                'size_inch', 'resolution', 'contrast', 'operation_temperature',
                'sunlight_readable', 'antiglare'
            ],
            'description': [
                'The name of the company that manufactures the product.',
                'The name of the product.',
                'The date when the product was manufactured.',
                'The size of the product in inches.',
                'The resolution of the product.',
                'The contrast ratio of the product.',
                'The recommended operating temperature range for the product.',
                'Indicates whether the product is readable in sunlight or not.',
                'Indicates whether the product has an anti-glare feature or not.'
            ]    
        }
        
        response_schemas = []
        for i in range(len(SCHEMAS['name'])):
            response_schemas.append(
                ResponseSchema(
                name=SCHEMAS['name'][i],
                description=SCHEMAS['description'][i]
                )
            )

        return response_schemas

    @property
    def get_prompt(self) -> PromptTemplate:
        # TODO: Use output_parser and schema (fuck langchain still not do well)
        prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=['context', 'question'],
        )

        return prompt

    @property
    def get_output_parser(self):
        response_schemas = self.get_schemas
        output_parser = StructuredOutputParser.from_response_schemas(
            response_schemas
        )
        return output_parser
