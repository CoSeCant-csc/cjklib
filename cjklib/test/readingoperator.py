#!/usr/bin/python
# -*- coding: utf-8 -*-
# This file is part of cjklib.
#
# cjklib is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cjklib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with cjklib.  If not, see <http://www.gnu.org/licenses/>.

"""
Provides the library's unit tests for the L{reading.operator} classes.
"""
import re
import types
import unittest

from cjklib.reading import ReadingFactory, operator
from cjklib import exception

class ReadingOperatorTest():
    """Base class for testing of L{ReadingOperator}s."""
    READING_NAME = None
    """Name of reading to test"""

    def setUp(self):
        self.f = ReadingFactory()

        for clss in self.f.getReadingOperatorClasses():
            if clss.READING_NAME == self.READING_NAME:
                self.readingOperatorClass = clss
                break
        else:
            self.readingOperatorClass = None

    def shortDescription(self):
        methodName = getattr(self, self.id().split('.')[-1])
        # get whole doc string and remove superfluous white spaces
        noWhitespaceDoc = re.sub('\s+', ' ', methodName.__doc__.strip())
        # remove markup for epytext format
        clearName = re.sub('[CL]\{([^\}]*)}', r'\1', noWhitespaceDoc)
        # add name of reading
        return clearName + ' (for %s)' % self.READING_NAME


class ReadingOperatorConsistencyTest(ReadingOperatorTest):
    """Base class for consistency testing of L{ReadingOperator}s."""
    DIALECTS = []
    """
    Dialects tested additionally to the standard one.
    Given as list of dictionaries holding the dialect's options.
    """

    def testReadingNameUnique(self):
        """Test if only one ReadingOperator exists for each reading."""
        seen = False

        for clss in self.f.getReadingOperatorClasses():
            if clss.READING_NAME == self.READING_NAME:
                self.assert_(not seen,
                    "Reading %s has more than one operator" \
                    % clss.READING_NAME)
                seen = True

    def testInstantiation(self):
        """Test if given dialects can be instantiated"""
        self.assert_(self.readingOperatorClass != None,
            "No reading operator class found" \
                + ' (reading %s)' % self.READING_NAME)

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            # instantiate
            self.readingOperatorClass(**dialect)

    def testDefaultOptions(self):
        """
        Test if option dict returned by C{getDefaultOptions()} is well-formed
        and includes all options found in the test case's options.
        """
        defaultOptions = self.readingOperatorClass.getDefaultOptions()

        self.assertEquals(type(defaultOptions), type({}),
            "Default options %s is not of type dict" % repr(defaultOptions) \
            + ' (reading %s)' % self.READING_NAME)
        # test if option names are well-formed
        for option in defaultOptions:
            self.assertEquals(type(option), type(''),
                "Option %s is not of type str" % repr(option) \
                + ' (reading %s)' % self.READING_NAME)

        # test all given dialects
        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            for option in dialect:
                self.assert_(option in defaultOptions,
                    "Test case option %s not found in default options" \
                        % repr(option) \
                    + ' (reading %s, dialect %s)' \
                        % (self.READING_NAME, dialect))

        # test instantiation of default options
        defaultInstance = self.readingOperatorClass(**defaultOptions)

        # check if option value changes after instantiation
        for option in defaultOptions:
            self.assertEqual(defaultInstance.getOption(option),
                defaultOptions[option],
                "Default option value %s for %s changed on instantiation: %s" \
                    % (repr(defaultOptions[option]), repr(option),
                        repr(defaultInstance.getOption(option))) \
                + ' (reading %s)' % self.READING_NAME)

        # check options against instance without explicit option dict
        instance = self.readingOperatorClass()
        for option in defaultOptions:
            self.assertEqual(instance.getOption(option),
                defaultInstance.getOption(option),
                "Option value for %s unequal for default instances: %s and %s" \
                    % (repr(option), repr(instance.getOption(option)),
                        repr(defaultInstance.getOption(option))) \
                + ' (reading %s)' % self.READING_NAME)

    def testGuessReadingDialect(self):
        """
        Test if option dict returned by C{guessReadingDialect()} is well-formed
        and options are included in dict from C{getDefaultOptions()}.
        """
        if not hasattr(self.readingOperatorClass, 'guessReadingDialect'):
            return

        defaultOptions = self.readingOperatorClass.getDefaultOptions()

        readingDialect = self.readingOperatorClass.guessReadingDialect('')

        self.assertEquals(type(defaultOptions), type({}),
            "Guessed options %s is not of type dict" % repr(readingDialect) \
            + ' (reading %s)' % self.READING_NAME)
        # test if option names are well-formed
        for option in readingDialect:
            self.assertEquals(type(option), type(''),
                "Option %s is not of type str" % repr(option) \
                + ' (reading %s)' % self.READING_NAME)

        # test inclusion in default set
        for option in readingDialect:
            self.assert_(option in defaultOptions,
                "Option %s not found in default options" % repr(option) \
                + ' (reading %s)' % self.READING_NAME)

        # test instantiation of default options
        defaultInstance = self.readingOperatorClass(**readingDialect)

    def testValidReadingEntitiesAccepted(self):
        """
        Test if all reading entities returned by C{getReadingEntities()} are
        accepted by C{isReadingEntity()}.
        """
        if not hasattr(self.readingOperatorClass, "getReadingEntities"):
            return

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            entities = self.f.getReadingEntities(self.READING_NAME,
                **dialect)
            for entity in entities:
                self.assert_(
                    self.f.isReadingEntity(entity, self.READING_NAME,
                        **dialect),
                    "Entity %s not accepted" % repr(entity) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))

    def testValidPlainReadingEntitiesAccepted(self):
        """
        Test if all plain reading entities returned by
        C{getPlainReadingEntities()} are accepted by C{isPlainReadingEntity()}.
        """
        if not hasattr(self.readingOperatorClass, "getPlainReadingEntities"):
            return

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            plainEntities = self.f.getPlainReadingEntities(self.READING_NAME,
                **dialect)
            for plainEntity in plainEntities:
                self.assert_(
                    self.f.isPlainReadingEntity(plainEntity, self.READING_NAME,
                        **dialect),
                    "Plain entity %s not accepted" % repr(plainEntity) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))

    def testOnsetRhyme(self):
        """Test if all plain entities are accepted by C{getOnsetRhyme()}."""
        if not hasattr(self.readingOperatorClass, "getPlainReadingEntities") \
            or not hasattr(self.readingOperatorClass, "testOnsetRhyme"):
            return

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            readingOperator = self.f.createReadingOperator(self.READING_NAME,
                **dialect)
            plainEntities = readingOperator.getPlainReadingEntities()
            for plainEntity in plainEntities:
                try:
                    result = readingOperator.getOnsetRhyme(plainEntity)
                except exception.InvalidEntityError:
                    self.fail("Plain entity %s not accepted" \
                        % repr(plainEntity) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))
                except exception.UnsupportedError:
                    pass

    def testDecomposeIsIdentityForSingleEntity(self):
        """
        Test if all reading entities returned by C{getReadingEntities()} are
        decomposed into the single entity again.
        """
        if not hasattr(self.readingOperatorClass, "getReadingEntities"):
            return

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            entities = self.f.getReadingEntities(self.READING_NAME, **dialect)
            for entity in entities:
                try:
                    entities = self.f.decompose(entity, self.READING_NAME,
                        **dialect)
                    self.assertEquals(entities, [entity],
                        "decomposition on single entity %s" % repr(entity) \
                        + " is not identical: %s" % repr(entities) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))
                except exception.AmbiguousDecompositonError:
                    self.fail("ambiguous decomposition for %s" % repr(entity) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))
                except exception.DecompositionError:
                    self.fail("decomposition error for %s" % repr(entity) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))


    def testGetTonalEntityOfSplitEntityToneIsIdentity(self):
        """
        Test if the composition of C{getTonalEntity()} and C{splitEntityTone()}
        returns the original value for all entities returned by
        C{getReadingEntities()}.
        """
        if not hasattr(self.readingOperatorClass, "getPlainReadingEntities"):
            return

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            entities = self.f.getReadingEntities(self.READING_NAME, **dialect)
            for entity in entities:
                try:
                    plainEntity, tone = self.f.splitEntityTone(entity,
                        self.READING_NAME, **dialect)

                    self.assertEquals(
                        self.f.getTonalEntity(plainEntity, tone,
                            self.READING_NAME, **dialect),
                        entity,
                        "Entity %s not preserved in composition" % repr(entity)\
                            + " of getTonalEntity() and splitEntityTone()" \
                            + ' (reading %s, dialect %s)' \
                                % (self.READING_NAME, dialect))
                except exception.UnsupportedError:
                    pass
                except exception.InvalidEntityError:
                    self.fail("Entity %s raised InvalidEntityError" \
                        % repr(entity) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))

    def testSplitEntityToneReturnsValidInformation(self):
        """
        Test if C{splitEntityTone()} returns a valid plain entity and a valid
        tone for all entities returned by C{getReadingEntities()}.
        """
        if not hasattr(self.readingOperatorClass, "getPlainReadingEntities"):
            return

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            entities = self.f.getReadingEntities(self.READING_NAME, **dialect)
            for entity in entities:
                try:
                    plainEntity, tone = self.f.splitEntityTone(entity,
                        self.READING_NAME, **dialect)

                    self.assert_(self.f.isPlainReadingEntity(plainEntity,
                        self.READING_NAME, **dialect),
                        "Plain entity of %s not accepted: %s" \
                            % (repr(entity), repr(plainEntity)) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))

                    self.assert_(
                        tone in self.f.getTones(self.READING_NAME, **dialect),
                        "Tone of entity %s not valid: %s " \
                            % (repr(entity), repr(tone)) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))
                except exception.UnsupportedError:
                    pass
                except exception.InvalidEntityError:
                    self.fail("Entity %s raised InvalidEntityError" \
                        % repr(entity) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))

    #TODO Jyutping (missing tone marks) and CantoneseYale don't create strict
      #compositions
    def testDecomposeKeepsSyllablePairs(self):
        """
        Test if all pairs of reading entities returned by
        C{getReadingEntities()} are decomposed into the same pairs again and
        possibly are strict.
        """
        if not hasattr(self.readingOperatorClass, "getReadingEntities"):
            return

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            entities = self.f.getReadingEntities(self.READING_NAME, **dialect)
            for entityA in entities:
                for entityB in entities:
                    pair = [entityA, entityB]
                    string = self.f.compose(pair, self.READING_NAME, **dialect)
                    try:
                        decomposition = self.f.decompose(string,
                            self.READING_NAME, **dialect)

                        if hasattr(self, 'cleanDecomposition'):
                            cleanDecomposition = self.cleanDecomposition(
                                decomposition, self.READING_NAME, **dialect)
                        else:
                            cleanDecomposition = decomposition

                        self.assertEquals(cleanDecomposition, pair,
                            "decompose doesn't keep entity pair %s: %s" \
                                % (repr(pair), repr(cleanDecomposition)) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))

                        # test if method exists and by default is not False
                        if hasattr(self.readingOperatorClass,
                            "isStrictDecomposition") \
                            and self.f.isStrictDecomposition([],
                                self.READING_NAME, **dialect) != False: # TODO this doesn't capture bugs in isStrictDecomposition that return False for an empty array

                            strict = self.f.isStrictDecomposition(decomposition,
                                self.READING_NAME, **dialect)

                            self.assert_(strict,
                                "Decomposition for pair %s is not strict" \
                                    % repr(string) \
                                + ' (reading %s, dialect %s)' \
                                    % (self.READING_NAME, dialect))

                    except exception.DecompositionError:
                        self.fail('Decomposition fails for pair %s' \
                            % repr(pair) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))


class ReadingOperatorTestCaseCheck(unittest.TestCase):
    """
    Checks if every L{ReadingOperator} has its own
    L{ReadingOperatorConsistencyTest}.
    """
    def testEveryOperatorHasConsistencyTest(self):
        """
        Check if every reading has a test case.
        """
        testClasses = self.getReadingOperatorConsistencyTestClasses()
        testClassReadingNames = [clss.READING_NAME for clss in testClasses]
        self.f = ReadingFactory()

        for clss in self.f.getReadingOperatorClasses():
            self.assert_(clss.READING_NAME in testClassReadingNames,
                "Reading %s has no ReadingOperatorConsistencyTest" \
                    % clss.READING_NAME)

    @staticmethod
    def getReadingOperatorConsistencyTestClasses():
        """
        Gets all classes implementing L{ReadingOperatorConsistencyTest}.

        @rtype: list
        @return: list of all classes inheriting form
            L{ReadingOperatorConsistencyTest}
        """
        # get all non-abstract classes that inherit from
        #   ReadingOperatorConsistencyTest
        testModule = __import__("cjklib.test.readingoperator")
        testClasses = [clss for clss \
            in testModule.test.readingoperator.__dict__.values() \
            if type(clss) == types.TypeType \
            and issubclass(clss, ReadingOperatorConsistencyTest) \
            and clss.READING_NAME]

        return testClasses


class ReadingOperatorReferenceTest(ReadingOperatorTest):
    """
    Base class for testing of references against L{ReadingOperator}s.
    These tests assure that the given values are returned correctly.
    """

    DECOMPOSITION_REFERENCES = []
    """
    References to test C{decompose()} operation.
    List of dialect/reference tuples, schema: ({dialect}, [(reference, target)])
    """

    COMPOSITION_REFERENCES = []
    """
    References to test C{compose()} operation.
    List of dialect/reference tuples, schema: ({}, [(reference, target)])
    """

    READING_ENTITY_REFERENCES = []
    """
    References to test C{isReadingEntity()} operation.
    List of dialect/reference tuples, schema: ({}, [(reference, target)])
    """

    GUESS_DIALECT_REFERENCES = []
    """
    References to test C{guessReadingDialect()} operation.
    List of reference/dialect tuples, schema: (reference, {})
    """

    def testDecompositionReferences(self):
        """Test if the given decomposition references are reached."""
        for dialect, references in self.DECOMPOSITION_REFERENCES:
            for reference, target in references:
                decomposition = self.f.decompose(reference, self.READING_NAME,
                    **dialect)
                self.assertEquals(decomposition, target,
                    "Decomposition %s of %s not reached: %s" \
                        % (repr(target), repr(reference), repr(decomposition)) \
                    + ' (reading %s, dialect %s)' \
                        % (self.READING_NAME, dialect))

    def testCompositionReferences(self):
        """Test if the given composition references are reached."""
        for dialect, references in self.COMPOSITION_REFERENCES:
            for reference, target in references:
                composition = self.f.compose(reference, self.READING_NAME,
                    **dialect)
                self.assertEquals(composition, target,
                    "Composition %s of %s not reached: %s" \
                        % (repr(target), repr(reference), repr(composition)) \
                    + ' (reading %s, dialect %s)' \
                        % (self.READING_NAME, dialect))

    def testEntityReferences(self):
        """Test if the given entity references are accepted/rejected."""
        for dialect, references in self.READING_ENTITY_REFERENCES:
            for reference, target in references:
                result = self.f.isReadingEntity(reference,
                    self.READING_NAME, **dialect)
                self.assertEquals(result, target,
                    "Target %s of %s not reached: %s" \
                        % (repr(target), repr(reference), repr(result)) \
                    + ' (reading %s, dialect %s)' \
                        % (self.READING_NAME, dialect))

    def testGuessDialectReferences(self):
        """Test if C{guessReadingDialect()} guesses the needed options."""
        if not hasattr(self.readingOperatorClass, 'guessReadingDialect'):
            return

        for reference, dialect in self.GUESS_DIALECT_REFERENCES:
            result = self.readingOperatorClass.guessReadingDialect(reference)
            for option, value in dialect.items():
                self.assert_(option in result,
                    "Guessed dialect doesn't include option  %s" \
                        % repr(option) \
                    + ' (reading %s, dialect %s)' \
                        % (self.READING_NAME, dialect))
                self.assertEquals(result[option], value,
                    "Target for option %s=%s not reached for %s: %s" \
                        % (repr(option), repr(value), repr(reference),
                            repr(result[option])) \
                    + ' (reading %s)' % self.READING_NAME)


class CanoneseIPAOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'CantoneseIPA'

    DIALECTS = [{'toneMarkType': 'Numbers'},
        {'toneMarkType': 'ChaoDigits'},
        # {'toneMarkType': 'Diacritics'}, # TODO NotImplementedError
        {'toneMarkType': 'None'},
        {'toneMarkType': 'Numbers', '1stToneName': 'HighFalling'},
        {'missingToneMark': 'ignore'},
        {'stopTones': 'general'},
        {'stopTones': 'explicit'},
        ]

    def cleanDecomposition(self, decomposition, reading, **options):
        return [entity for entity in decomposition if entity != '.']

    def testEntityCountConstant(self):
        """
        Test if the number of reading entities reported by
        C{getReadingEntities()} is constant between different stop tone
        realisations.
        """
        if not hasattr(self.readingOperatorClass, "getReadingEntities"):
            return

        entityCount = None
        for stopTones in ['none', 'general', 'explicit']:
            count = len(self.f.getReadingEntities(self.READING_NAME,
                stopTones=stopTones))
            if entityCount != None:
                self.assertEquals(entityCount, count)

    def testReportedToneValid(self):
        """
        Test if the tone reported by C{splitEntityTone()} is valid for the given
        entity.
        """
        if not hasattr(self.readingOperatorClass, "isToneValid"):
            return

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            ipaOperator = self.f.createReadingOperator(self.READING_NAME,
                **dialect)

            entities = ipaOperator.getReadingEntities()
            for entity in entities:
                plainEntity, tone = ipaOperator.splitEntityTone(entity)

                self.assert_(ipaOperator.isToneValid(plainEntity, tone),
                    "Tone %s is invalid with plain entity %s" \
                        % (repr(tone), repr(plainEntity)) \
                    + ' (reading %s, dialect %s)' \
                        % (self.READING_NAME, dialect))

    def testBaseExplicitTones(self):
        """
        Test if the tones reported by C{getBaseTone()} and C{getExplicitTone()}
        are valid.
        """
        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            ipaOperator = self.f.createReadingOperator(self.READING_NAME,
                **dialect)
            for tone in ipaOperator.getTones():
                tone = ipaOperator.getBaseTone(tone)
                self.assert_(tone == None or tone in ipaOperator.TONES)

            entities = ipaOperator.getPlainReadingEntities()
            for plainEntity in entities:
                for tone in ipaOperator.getTones():
                    try:
                        explicitTone = ipaOperator.getExplicitTone(plainEntity,
                            tone)
                        self.assert_(explicitTone == None \
                            or explicitTone in ipaOperator.TONES \
                            or explicitTone in ipaOperator.STOP_TONES_EXPLICIT)
                    except exception.InvalidEntityError:
                        pass

# TODO
#class CantoneseIPAOperatorReferenceTest(ReadingOperatorReferenceTest,
    #unittest.TestCase):
    #READING_NAME = 'CantoneseIPA'

    #DECOMPOSITION_REFERENCES = []

    #COMPOSITION_REFERENCES = []

    #READING_ENTITY_REFERENCES = []


class CanoneseYaleOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'CantoneseYale'

    DIALECTS = [{'toneMarkType': 'Numbers'},
        {'toneMarkType': 'Numbers', 'missingToneMark': 'ignore'},
        {'toneMarkType': 'Numbers', 'missingToneMark': 'ignore',
            'strictSegmentation': True},
        {'toneMarkType': 'Numbers', 'YaleFirstTone': '1stToneFalling'},
        {'toneMarkType': 'None'},
        {'strictDiacriticPlacement': True},
        {'strictSegmentation': True},
        {'case': 'lower'},
        ]


# TODO
class CantoneseYaleOperatorReferenceTest(ReadingOperatorReferenceTest,
    unittest.TestCase):
    READING_NAME = 'CantoneseYale'

    DECOMPOSITION_REFERENCES = [
        ({}, [
            (u'gwóngjàuwá', [u'gwóng', u'jàu', u'wá']),
            (u'yuhtyúh', [u'yuht', u'yúh']),
            (u'néihhóu', [u'néih', u'hóu']),
            (u'gwóngjaù', [u'gwóng', u'jaù']), # wrong placement of tone
            (u'GWÓNGJÀUWÁ', [u'GWÓNG', u'JÀU', u'WÁ']),
            (u'sīsísisìhsíhsihsīksiksihk', [u'sī', u'sí', u'si', u'sìh', u'síh',
                u'sih', u'sīk', u'sik', u'sihk']),
            (u'SÌSÍSISÌHSÍHSIHSĪKSIKSIHK', [u'SÌ', u'SÍ', u'SI', u'SÌH', u'SÍH',
                u'SIH', u'SĪK', u'SIK', u'SIHK']),
            ]),
        ({'toneMarkType': 'Numbers'}, [
            (u'gwong2jau1wa2', [u'gwong2', u'jau1', u'wa2']),
            (u'yut6yu5', [u'yut6', u'yu5']),
            (u'nei5hou2', [u'nei5', u'hou2']),
            (u'GWONG2JAU1WA2', [u'GWONG2', u'JAU1', u'WA2']),
            (u'si1si2si3si4si5si6sik1sik3sik6', [u'si1', u'si2', u'si3', u'si4',
                u'si5', u'si6', u'sik1', u'sik3', u'sik6']),
            (u'SI1SI2SI3SI4SI5SI6SIK1SIK3SIK6', [u'SI1', u'SI2', u'SI3', u'SI4',
                u'SI5', u'SI6', u'SIK1', u'SIK3', u'SIK6']),
            ]),
        ({'strictDiacriticPlacement': True}, [
            (u'gwóngjàuwá', [u'gwóng', u'jàu', u'wá']),
            (u'yuhtyúh', [u'yuht', u'yúh']),
            (u'néihhóu', [u'néih', u'hóu']),
            (u'gwóngjaù', [u'gwóngjaù']), # wrong placement of tone
            ])
        ]
    COMPOSITION_REFERENCES = []

    READING_ENTITY_REFERENCES = [
        ({}, [
            (u'wā', True),
            (u'gwóng', True),
            (u'jàu', True),
            (u'wá', True),
            (u'néih', True),
            (u'yuht', True),
            (u'gwong', True),
            (u'wa\u0304', True),
            (u'jaù', True),
            (u'gwongh', True),
            (u'wáa', False),
            (u'GWÓNG', True),
            (u'SIK', True),
            (u'bàt', False), # stop tone
            (u'bat4', False), # stop tone
            ]),
        ({'strictDiacriticPlacement': True}, [
            (u'wā', True),
            (u'gwóng', True),
            (u'jàu', True),
            (u'wá', True),
            (u'néih', True),
            (u'yuht', True),
            (u'gwong', True),
            (u'wa\u0304', True),
            (u'jaù', False),
            (u'gwongh', False),
            (u'wáa', False),
            (u'GWÓNG', True),
            (u'SIK', True),
            (u'bàt', False), # stop tone
            (u'bat4', False), # stop tone
            ]),
        ({'case': 'lower'}, [
            (u'wā', True),
            (u'gwóng', True),
            (u'jàu', True),
            (u'wá', True),
            (u'néih', True),
            (u'yuht', True),
            (u'gwong', True),
            (u'wa\u0304', True),
            (u'jaù', True),
            (u'gwongh', True),
            (u'wáa', False),
            (u'GWÓNG', False),
            (u'SIK', False),
            (u'bàt', False), # stop tone
            (u'bat4', False), # stop tone
            ]),
        ]

    GUESS_DIALECT_REFERENCES = []


class JyutpingOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'Jyutping'

    DIALECTS = [{'toneMarkType': 'None'},
        {'missingToneMark': 'ignore'},
        {'missingToneMark': 'ignore', 'strictSegmentation': True},
        {'strictSegmentation': True},
        {'case': 'lower'},
        ]


# TODO
class JyutpingOperatorReferenceTest(ReadingOperatorReferenceTest,
    unittest.TestCase):
    READING_NAME = 'Jyutping'

    DECOMPOSITION_REFERENCES = [
        ({}, [
            (u'gwong2zau1waa2', [u'gwong2', u'zau1', u'waa2']),
            ]),
        ]

    COMPOSITION_REFERENCES = []

    READING_ENTITY_REFERENCES = [
        ({}, [
            (u'si1', True),
            (u'si2', True),
            (u'si3', True),
            (u'si4', True),
            (u'si5', True),
            (u'si6', True),
            (u'sik1', True),
            (u'sik2', False), # stop tone
            (u'sik3', True),
            (u'sik4', False), # stop tone
            (u'sik5', False), # stop tone
            (u'sik6', True),
            ]),
        ]


class HangulOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'Hangul'


# TODO
class HangulOperatorReferenceTest(ReadingOperatorReferenceTest,
    unittest.TestCase):
    READING_NAME = 'Hangul'

    DECOMPOSITION_REFERENCES = [
        ({}, [
            (u"한글은 한국어의 고유", [u"한", u"글", u"은", u" ",
                u"한", u"국", u"어", u"의", u" ", u"고", u"유"]),
            ]),
        ]

    COMPOSITION_REFERENCES = []

    READING_ENTITY_REFERENCES = []


class HiraganaOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'Hiragana'


# TODO
#class HiraganaOperatorReferenceTest(ReadingOperatorReferenceTest,
    #unittest.TestCase):
    #READING_NAME = 'Hiragana'

    #DECOMPOSITION_REFERENCES = []

    #COMPOSITION_REFERENCES = []

    #READING_ENTITY_REFERENCES = []


class KatakanaOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'Katakana'


# TODO
#class KatakanaOperatorReferenceTest(ReadingOperatorReferenceTest,
    #unittest.TestCase):
    #READING_NAME = 'Katakana'

    #DECOMPOSITION_REFERENCES = []

    #COMPOSITION_REFERENCES = []

    #READING_ENTITY_REFERENCES = []


class KanaOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'Kana'


# TODO
#class KanaOperatorReferenceTest(ReadingOperatorReferenceTest,
    #unittest.TestCase):
    #READING_NAME = 'Kana'

    #DECOMPOSITION_REFERENCES = []

    #COMPOSITION_REFERENCES = []

    #READING_ENTITY_REFERENCES = []


class PinyinOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'Pinyin'

    def noToneApostropheRule(precedingEntity, followingEntity):
        return precedingEntity and precedingEntity[0].isalpha() \
            and not precedingEntity[-1].isdigit() \
            and followingEntity[0].isalpha()

    DIALECTS = [{'toneMarkType': 'Numbers'},
        {'toneMarkType': 'Numbers', 'missingToneMark': 'fifth'},
        {'toneMarkType': 'Numbers', 'missingToneMark': 'ignore'},
        {'toneMarkType': 'Numbers', 'missingToneMark': 'ignore',
            'strictSegmentation': True},
        {'toneMarkType': 'Numbers', 'yVowel': 'v'},
        {'toneMarkType': 'None'},
        {'PinyinApostrophe': u'’'},
        {'toneMarkType': 'Numbers',
            'PinyinApostropheFunction': noToneApostropheRule},
        {'Erhua': 'oneSyllable'},
        {'strictDiacriticPlacement': True},
        {'strictSegmentation': True},
        {'case': 'lower'},
        ]

    def cleanDecomposition(self, decomposition, reading, **options):
        if not hasattr(self, '_operators'):
            self._operators = []
        for operatorReading, operatorOptions, op in self._operators:
            if reading == operatorReading and options == operatorOptions:
                break
        else:
            op = self.f.createReadingOperator(reading, **options)
            self._operators.append((reading, options, op))

        return op.removeApostrophes(decomposition)


class PinyinOperatorReferenceTest(ReadingOperatorReferenceTest,
    unittest.TestCase):
    READING_NAME = 'Pinyin'

    DECOMPOSITION_REFERENCES = [
        ({}, [
            (u"tiān'ānmén", [u"tiān", "'", u"ān", u"mén"]),
            ("xian", ["xian"]),
            (u"xīān", [u"xī", u"ān"]),
            (u"tian1'an1men2", [u"tian1", "'", u"an1", u"men2"]),
            (u"tian'anmen", [u"tian", "'", u"an", u"men"]),
            (u"xi1an1", [u"xi1", u"an1"]),
            (u"lao3tou2r5", [u"lao3", u"tou2", u"r5"]),
            (u"lao3tour2", [u"lao3", u"tour2"]),
            (u"er2hua4yin1", [u"er2", u"hua4", u"yin1"]),
            (u"peínǐ", [u'peí', u'nǐ']), # wrong placement of tone
            (u"hónglùo", [u'hóng', u'lùo']), # wrong placement of tone
            (u"Tiān'ānmén", [u"Tiān", "'", u"ān", u"mén"]),
            (u"TIĀN'ĀNMÉN", [u"TIĀN", "'", u"ĀN", u"MÉN"]),
            ("XIAN", ["XIAN"]),
            (u"TIAN1'AN1MEN2", [u"TIAN1", "'", u"AN1", u"MEN2"]),
            ]),
        ({'toneMarkType': 'Numbers'}, [
            (u"tiān'ānmén", [u"tiān", "'", u"ānmén"]),
            ("xian", ["xian"]),
            (u"xīān", [u"xīān"]),
            (u"tian1'an1men2", [u"tian1", "'", u"an1", u"men2"]),
            (u"tian'anmen", [u"tian", "'", u"an", u"men"]),
            (u"xi1an1", [u"xi1", u"an1"]),
            (u"lao3tou2r5", [u"lao3", u"tou2", u"r5"]),
            (u"lao3tour2", [u"lao3", u"tour2"]),
            (u"er2hua4yin1", [u"er2", u"hua4", u"yin1"]),
            (u"peínǐ", [u'peínǐ']), # wrong placement of tone
            (u"hónglùo", [u'hónglùo']), # wrong placement of tone
            (u"Tiān'ānmén", [u"Tiān", "'", u"ānmén"]),
            (u"TIĀN'ĀNMÉN", [u"TIĀN", "'", u"ĀNMÉN"]),
            ("XIAN", ["XIAN"]),
            (u"TIAN1'AN1MEN2", [u"TIAN1", "'", u"AN1", u"MEN2"]),
            ]),
        ({'toneMarkType': 'Numbers', 'missingToneMark': 'ignore'}, [
            (u"tiān'ānmén", [u"tiān", "'", u"ānmén"]),
            ("xian", ["xian"]),
            (u"xīān", [u"xīān"]),
            (u"tian1'an1men2", [u"tian1", "'", u"an1", u"men2"]),
            (u"tian'anmen", [u"tian", "'", u"anmen"]),
            (u"xi1an1", [u"xi1", u"an1"]),
            (u"lao3tou2r5", [u"lao3", u"tou2", u"r5"]),
            (u"lao3tour2", [u"lao3", u"tour2"]),
            (u"er2hua4yin1", [u"er2", u"hua4", u"yin1"]),
            (u"peínǐ", [u'peínǐ']), # wrong placement of tone
            (u"hónglùo", [u'hónglùo']), # wrong placement of tone
            (u"Tiān'ānmén", [u"Tiān", "'", u"ānmén"]),
            (u"TIĀN'ĀNMÉN", [u"TIĀN", "'", u"ĀNMÉN"]),
            ("XIAN", ["XIAN"]),
            (u"TIAN1'AN1MEN2", [u"TIAN1", "'", u"AN1", u"MEN2"]),
            ]),
        ({'Erhua': 'oneSyllable'}, [
            (u"tiān'ānmén", [u"tiān", "'", u"ān", u"mén"]),
            ("xian", ["xian"]),
            (u"xīān", [u"xī", u"ān"]),
            (u"tian1'an1men2", [u"tian1", "'", u"an1", u"men2"]),
            (u"tian'anmen", [u"tian", "'", u"an", u"men"]),
            (u"xi1an1", [u"xi1", u"an1"]),
            (u"lao3tou2r5", [u"lao3", u"tou2", u"r5"]),
            (u"lao3tour2", [u"lao3", u"tour2"]),
            (u"er2hua4yin1", [u"er2", u"hua4", u"yin1"]),
            (u"peínǐ", [u'peí', u'nǐ']), # wrong placement of tone
            (u"hónglùo", [u'hóng', u'lùo']), # wrong placement of tone
            (u"Tiān'ānmén", [u"Tiān", "'", u"ān", u"mén"]),
            (u"TIĀN'ĀNMÉN", [u"TIĀN", "'", u"ĀN", u"MÉN"]),
            ("XIAN", ["XIAN"]),
            (u"TIAN1'AN1MEN2", [u"TIAN1", "'", u"AN1", u"MEN2"]),
            ]),
        ({'strictDiacriticPlacement': True}, [
            (u"tiān'ānmén", [u"tiān", "'", u"ān", u"mén"]),
            ("xian", ["xian"]),
            (u"xīān", [u"xī", u"ān"]),
            (u"tian1'an1men2", [u"tian1", "'", u"an1", u"men2"]),
            (u"tian'anmen", [u"tian", "'", u"an", u"men"]),
            (u"xi1an1", [u"xi1", u"an1"]),
            (u"lao3tou2r5", [u"lao3", u"tou2", u"r5"]),
            (u"lao3tour2", [u"lao3", u"tour2"]),
            (u"er2hua4yin1", [u"er2", u"hua4", u"yin1"]),
            (u"peínǐ", [u'peínǐ']), # wrong placement of tone
            (u"hónglùo", [u'hóng', u'lù', u'o']), # wrong placement of tone
            (u"Tiān'ānmén", [u"Tiān", "'", u"ān", u"mén"]),
            (u"TIĀN'ĀNMÉN", [u"TIĀN", "'", u"ĀN", u"MÉN"]),
            ("XIAN", ["XIAN"]),
            (u"TIAN1'AN1MEN2", [u"TIAN1", "'", u"AN1", u"MEN2"]),
            ]),
        ({'case': 'lower'}, [
            (u"tiān'ānmén", [u"tiān", "'", u"ān", u"mén"]),
            ("xian", ["xian"]),
            (u"xīān", [u"xī", u"ān"]),
            (u"tian1'an1men2", [u"tian1", "'", u"an1", u"men2"]),
            (u"tian'anmen", [u"tian", "'", u"an", u"men"]),
            (u"xi1an1", [u"xi1", u"an1"]),
            (u"lao3tou2r5", [u"lao3", u"tou2", u"r5"]),
            (u"lao3tour2", [u"lao3", u"tour2"]),
            (u"er2hua4yin1", [u"er2", u"hua4", u"yin1"]),
            (u"peínǐ", [u'peí', u'nǐ']), # wrong placement of tone
            (u"hónglùo", [u'hóng', u'lùo']), # wrong placement of tone
            (u"Tiān'ānmén", [u"Tiān", "'", u"ān", u"mén"]),
            (u"TIĀN'ĀNMÉN", [u"TIĀN", "'", u"ĀNMÉN"]),
            ("XIAN", ["XIAN"]),
            (u"TIAN1'AN1MEN2", [u"TIAN1", "'", u"AN1", u"MEN2"]),
            ]),
        ]

    COMPOSITION_REFERENCES = [
        ({}, [
            ([u"tiān", u"ān", u"mén"], u"tiān'ānmén"),
            (["xian"], "xian"),
            ([u"xī", u"ān"], u"xī'ān"),
            ([u"tian1", "'", u"an1", u"men2"], u"tian1'an1men2"),
            ([u"tian1", u"an1", u"men2"], u"tian1an1men2"),
            ([u"tian", u"an", u"men"], u"tian'anmen"),
            ([u"xi1", u"an1"], u"xi1an1"),
            ([u"lao3", u"tou2", u"r5"], u"lao3tou2r5"),
            ([u"lao3", u"tour2"], u"lao3tour2"),
            ([u"lao3", u"angr2"], u"lao3angr2"),
            ([u"lao3", u"ang2", u"r5"], u"lao3ang2r5"),
            ([u"er2", u"hua4", u"yin1"], u"er2hua4yin1"),
            ([u'peí', u'nǐ'], u"peínǐ"), # wrong placement of tone
            ([u'hóng', u'lùo'], u"hónglùo"), # wrong placement of tone
            ([u"TIĀN", u"ĀN", u"MÉN"], u"TIĀN'ĀNMÉN"),
            ([u"TIAN1", u"AN1", u"MEN2"], u"TIAN1AN1MEN2", ),
            ([u"e", u"r"], u"e'r"),
            ]),
        ({'toneMarkType': 'Numbers'}, [
            ([u"tiān", u"ān", u"mén"], u"tiānānmén"),
            (["xian"], "xian"),
            ([u"xī", u"ān"], u"xīān"),
            ([u"tian1", "'", u"an1", u"men2"], u"tian1'an1men2"),
            ([u"tian1", u"an1", u"men2"], u"tian1'an1men2"),
            ([u"tian", u"an", u"men"], u"tian'anmen"),
            ([u"xi1", u"an1"], u"xi1'an1"),
            ([u"lao3", u"tou2", u"r5"], u"lao3tou2r5"),
            ([u"lao3", u"tour2"], u"lao3tour2"),
            ([u"lao3", u"angr2"], u"lao3angr2"),
            ([u"lao3", u"ang2", u"r5"], u"lao3'ang2r5"),
            ([u"er2", u"hua4", u"yin1"], u"er2hua4yin1"),
            ([u'peí', u'nǐ'], u"peínǐ"), # wrong placement of tone
            ([u'hóng', u'lùo'], u"hónglùo"), # wrong placement of tone
            ([u"TIĀN", u"ĀN", u"MÉN"], u"TIĀNĀNMÉN"),
            ([u"TIAN1", u"AN1", u"MEN2"], u"TIAN1'AN1MEN2", ),
            ([u"e", u"r"], u"e'r"),
            ]),
        ({'toneMarkType': 'Numbers', 'missingToneMark': 'ignore'}, [
            ([u"tiān", u"ān", u"mén"], u"tiānānmén"),
            (["xian"], "xian"),
            ([u"xī", u"ān"], u"xīān"),
            ([u"tian1", "'", u"an1", u"men2"], u"tian1'an1men2"),
            ([u"tian1", u"an1", u"men2"], u"tian1'an1men2"),
            ([u"tian", u"an", u"men"], u"tiananmen"),
            ([u"xi1", u"an1"], u"xi1'an1"),
            ([u"lao3", u"tou2", u"r5"], u"lao3tou2r5"),
            ([u"lao3", u"tour2"], u"lao3tour2"),
            ([u"lao3", u"angr2"], u"lao3angr2"),
            ([u"lao3", u"ang2", u"r5"], u"lao3'ang2r5"),
            ([u"er2", u"hua4", u"yin1"], u"er2hua4yin1"),
            ([u'peí', u'nǐ'], u"peínǐ"), # wrong placement of tone
            ([u'hóng', u'lùo'], u"hónglùo"), # wrong placement of tone
            ([u"TIĀN", u"ĀN", u"MÉN"], u"TIĀNĀNMÉN"),
            ([u"TIAN1", u"AN1", u"MEN2"], u"TIAN1'AN1MEN2", ),
            ([u"e5", u"r5"], u"e5'r5"),
            ]),
        ({'Erhua': 'oneSyllable'}, [
            ([u"tiān", u"ān", u"mén"], u"tiān'ānmén"),
            (["xian"], "xian"),
            ([u"xī", u"ān"], u"xī'ān"),
            ([u"tian1", "'", u"an1", u"men2"], u"tian1'an1men2"),
            ([u"tian1", u"an1", u"men2"], u"tian1an1men2"),
            ([u"tian", u"an", u"men"], u"tian'anmen"),
            ([u"xi1", u"an1"], u"xi1an1"),
            ([u"lao3", u"tou2", u"r5"], u"lao3tou2r5"),
            ([u"lao3", u"tour2"], u"lao3tour2"),
            ([u"lao3", u"angr2"], u"lao3angr2"),
            ([u"lao3", u"ang2", u"r5"], u"lao3ang2r5"),
            ([u"er2", u"hua4", u"yin1"], u"er2hua4yin1"),
            ([u'peí', u'nǐ'], u"peínǐ"), # wrong placement of tone
            ([u'hóng', u'lùo'], u"hónglùo"), # wrong placement of tone
            ([u"TIĀN", u"ĀN", u"MÉN"], u"TIĀN'ĀNMÉN"),
            ([u"TIAN1", u"AN1", u"MEN2"], u"TIAN1AN1MEN2", ),
            ([u"e", u"r"], u"er"), # TODO
            ]),
        ({'toneMarkType': 'Numbers', 'Erhua': 'oneSyllable'}, [
            ([u"tiān", u"ān", u"mén"], u"tiānānmén"),
            (["xian"], "xian"),
            ([u"xī", u"ān"], u"xīān"),
            ([u"tian1", "'", u"an1", u"men2"], u"tian1'an1men2"),
            ([u"tian1", u"an1", u"men2"], u"tian1'an1men2"),
            ([u"tian", u"an", u"men"], u"tian'anmen"),
            ([u"xi1", u"an1"], u"xi1'an1"),
            ([u"lao3", u"tou2", u"r5"], u"lao3tou2r5"),
            ([u"lao3", u"tour2"], u"lao3tour2"),
            ([u"lao3", u"angr2"], u"lao3'angr2"),
            ([u"lao3", u"ang2", u"r5"], u"lao3'ang2r5"),
            ([u"er2", u"hua4", u"yin1"], u"er2hua4yin1"),
            ([u'peí', u'nǐ'], u"peínǐ"), # wrong placement of tone
            ([u'hóng', u'lùo'], u"hónglùo"), # wrong placement of tone
            ([u"TIĀN", u"ĀN", u"MÉN"], u"TIĀNĀNMÉN"),
            ([u"TIAN1", u"AN1", u"MEN2"], u"TIAN1'AN1MEN2", ),
            ([u"e", u"r"], u"er"), # TODO
            ]),
        ({'strictDiacriticPlacement': True}, [
            ([u"tiān", u"ān", u"mén"], u"tiān'ānmén"),
            (["xian"], "xian"),
            ([u"xī", u"ān"], u"xī'ān"),
            ([u"tian1", "'", u"an1", u"men2"], u"tian1'an1men2"),
            ([u"tian1", u"an1", u"men2"], u"tian1an1men2"),
            ([u"tian", u"an", u"men"], u"tian'anmen"),
            ([u"xi1", u"an1"], u"xi1an1"),
            ([u"lao3", u"tou2", u"r5"], u"lao3tou2r5"),
            ([u"lao3", u"tour2"], u"lao3tour2"),
            ([u"lao3", u"angr2"], u"lao3angr2"),
            ([u"lao3", u"ang2", u"r5"], u"lao3ang2r5"),
            ([u"er2", u"hua4", u"yin1"], u"er2hua4yin1"),
            ([u'peí', u'nǐ'], u"peínǐ"), # wrong placement of tone
            ([u'hóng', u'lùo'], u"hónglùo"), # wrong placement of tone
            ([u"TIĀN", u"ĀN", u"MÉN"], u"TIĀN'ĀNMÉN"),
            ([u"TIAN1", u"AN1", u"MEN2"], u"TIAN1AN1MEN2", ),
            ([u"e", u"r"], u"e'r"),
            ]),
        ]

    READING_ENTITY_REFERENCES = [
        ({}, [
            (u"tiān", True),
            (u"ān", True),
            (u"mén", True),
            (u"lào", True),
            (u"xǐ", True),
            (u"tian1", False),
            (u"an1", False),
            (u"men2", False),
            (u"lao4", False),
            (u"xi3", False),
            (u"xian", True),
            (u"ti\u0304an", True),
            (u"tia\u0304n", True),
            (u"laǒ", True),
            (u"tīan", True),
            (u"tīa", False),
            (u"tiā", False),
            (u"angr", False),
            (u"er", True),
            (u"r", True),
            (u"TIĀN", True),
            (u"XIAN", True),
            (u"TIAN1", False),
            (u"r1", False),
            ]),
        ({'toneMarkType': 'Numbers'}, [
            (u"tiān", False),
            (u"ān", False),
            (u"mén", False),
            (u"lào", False),
            (u"xǐ", False),
            (u"tian1", True),
            (u"an1", True),
            (u"men2", True),
            (u"lao4", True),
            (u"xi3", True),
            (u"xian", True),
            (u"ti\u0304an", False),
            (u"tia\u0304n", False),
            (u"laǒ", False),
            (u"tīan", False),
            (u"tīa", False),
            (u"tiā", False),
            (u"angr", False),
            (u"er", True),
            (u"r", True),
            (u"TIĀN", False),
            (u"XIAN", True),
            (u"TIAN1", True),
            (u"r1", False),
            ]),
        ({'toneMarkType': 'Numbers', 'missingToneMark': 'ignore'}, [
            (u"tiān", False),
            (u"ān", False),
            (u"mén", False),
            (u"lào", False),
            (u"xǐ", False),
            (u"tian1", True),
            (u"an1", True),
            (u"men2", True),
            (u"lao4", True),
            (u"xi3", True),
            (u"xian", False),
            (u"ti\u0304an", False),
            (u"tia\u0304n", False),
            (u"laǒ", False),
            (u"tīan", False),
            (u"tīa", False),
            (u"tiā", False),
            (u"angr", False),
            (u"er", False),
            (u"r", False),
            (u"TIĀN", False),
            (u"XIAN", False),
            (u"TIAN1", True),
            (u"r1", False),
            ]),
        ({'Erhua': 'oneSyllable'}, [
            (u"tiān", True),
            (u"ān", True),
            (u"mén", True),
            (u"lào", True),
            (u"xǐ", True),
            (u"tian1", False),
            (u"an1", False),
            (u"men2", False),
            (u"lao4", False),
            (u"xi3", False),
            (u"xian", True),
            (u"ti\u0304an", True),
            (u"tia\u0304n", True),
            (u"laǒ", True),
            (u"tīan", True),
            (u"tīa", False),
            (u"tiā", False),
            (u"angr", True),
            (u"er", True),
            (u"r", False),
            (u"TIĀN", True),
            (u"XIAN", True),
            (u"TIAN1", False),
            (u"r1", False),
            ]),
        ({'strictDiacriticPlacement': True}, [
            (u"tiān", True),
            (u"ān", True),
            (u"mén", True),
            (u"lào", True),
            (u"xǐ", True),
            (u"tian1", False),
            (u"an1", False),
            (u"men2", False),
            (u"lao4", False),
            (u"xi3", False),
            (u"xian", True),
            (u"tia\u0304n", True),
            (u"ti\u0304an", False),
            (u"laǒ", False),
            (u"tīan", False),
            (u"tīa", False),
            (u"tiā", False),
            (u"angr", False),
            (u"er", True),
            (u"r", True),
            (u"TIĀN", True),
            (u"XIAN", True),
            (u"TIAN1", False),
            (u"r1", False),
            ]),
        ({'case': 'lower'}, [
            (u"tiān", True),
            (u"ān", True),
            (u"mén", True),
            (u"lào", True),
            (u"xǐ", True),
            (u"tian1", False),
            (u"an1", False),
            (u"men2", False),
            (u"lao4", False),
            (u"xi3", False),
            (u"xian", True),
            (u"ti\u0304an", True),
            (u"tia\u0304n", True),
            (u"laǒ", True),
            (u"tīan", True),
            (u"tīa", False),
            (u"tiā", False),
            (u"angr", False),
            (u"er", True),
            (u"r", True),
            (u"TIĀN", False),
            (u"XIAN", False),
            (u"TIAN1", False),
            (u"r1", False),
            ]),
        ]

    STRICT_DECOMPOSITION_REFERENCES = [
        ({}, [
            ([u"tiān", "'", u"ān", u"mén"], True),
            ([u"tiān", u"ān", u"mén"], False),
            ([u"chan", u"gan"], True),
            (["xian"], True),
            ([u"tian1", u"an1", u"men2"], True),
            ([u"tian", u"an", u"men"], False),
            ([u"tian", "'", u"an", u"men"], True),
            ([u"lao3", u"angr2"], True),
            ([u"lao3", u"ang2", u"r5"], True),
            ([u"TIĀN", u"ĀN", u"MÉN"], False),
            ([u"TIAN1", u"AN1", u"MEN2"], True),
            ]),
        ({'toneMarkType': 'Numbers'}, [
            ([u"tiān", "'", u"ān", u"mén"], True),
            ([u"tiān", u"ān", u"mén"], True),
            ([u"chan", u"gan"], True),
            (["xian"], True),
            ([u"tian1", u"an1", u"men2"], False),
            ([u"tian", u"an", u"men"], False),
            ([u"tian", "'", u"an", u"men"], True),
            ([u"lao3", u"angr2"], True),
            ([u"lao3", u"ang2", u"r5"], False),
            ([u"TIĀN", u"ĀN", u"MÉN"], True),
            ([u"TIAN1", u"AN1", u"MEN2"], False),
            ]),
        ({'toneMarkType': 'Numbers', 'missingToneMark': 'ignore'}, [
            ([u"tiān", "'", u"ān", u"mén"], True),
            ([u"tiān", u"ān", u"mén"], True),
            ([u"chan", u"gan"], True),
            (["xian"], True),
            ([u"tian1", u"an1", u"men2"], False),
            ([u"tian", u"an", u"men"], True),
            ([u"tian", "'", u"an", u"men"], True),
            ([u"lao3", u"angr2"], True),
            ([u"lao3", u"ang2", u"r5"], False),
            ([u"TIĀN", u"ĀN", u"MÉN"], True),
            ([u"TIAN1", u"AN1", u"MEN2"], False),
            ]),
        ({'toneMarkType': 'Numbers', 'Erhua': 'oneSyllable'}, [
            ([u"tiān", "'", u"ān", u"mén"], True),
            ([u"tiān", u"ān", u"mén"], True),
            ([u"chan", u"gan"], True),
            (["xian"], True),
            ([u"tian1", u"an1", u"men2"], False),
            ([u"tian", u"an", u"men"], False),
            ([u"tian", "'", u"an", u"men"], True),
            ([u"lao3", u"angr2"], False),
            ([u"lao3", u"ang2", u"r5"], False),
            ([u"TIĀN", u"ĀN", u"MÉN"], True),
            ([u"TIAN1", u"AN1", u"MEN2"], False),
            ]),
        ]

    GUESS_DIALECT_REFERENCES = [
        (u"tiān'ānmén", {'toneMarkType': 'Diacritics',
            'PinyinApostrophe': "'"}),
        (u"tiān’ānmén", {'toneMarkType': 'Diacritics',
            'PinyinApostrophe': u"’"}),
        (u"xīān", {'toneMarkType': 'Diacritics'}),
        (u"tian1'an1men2", {'toneMarkType': 'Numbers',
            'PinyinApostrophe': "'"}),
        (u"nv3hai2", {'toneMarkType': 'Numbers', 'yVowel': 'v'}),
        (u"NV3HAI2", {'toneMarkType': 'Numbers', 'yVowel': 'v'}),
        (u"nǚhái", {'toneMarkType': 'Diacritics', 'yVowel': u'ü'}),
        (u"NǙHÁI", {'toneMarkType': 'Diacritics', 'yVowel': u'ü'}),
        (u"xi1'an1", {'toneMarkType': 'Numbers', 'PinyinApostrophe': "'"}),
        (u"lao3tou2r5", {'toneMarkType': 'Numbers',
            'Erhua': 'twoSyllables'}),
        (u"lao3tour2", {'toneMarkType': 'Numbers', 'Erhua': 'oneSyllable'}),
        (u"peínǐ", {'toneMarkType': 'Diacritics'}), # wrong placement of tone
        (u"TIĀNĀNMÉN", {'toneMarkType': 'Diacritics'}),
        (u"e5'r5", {'toneMarkType': 'Numbers', 'PinyinApostrophe': "'",
            'Erhua': 'twoSyllables'}),
        (u"yi xia r ", {'toneMarkType': 'Numbers', 'Erhua': 'twoSyllables'}),
        ]

    def testStrictDecompositionReferences(self):
        """Test if the given decomposition references pass strictness test."""
        for dialect, references in self.STRICT_DECOMPOSITION_REFERENCES:
            pinyinOperator = self.f.createReadingOperator(self.READING_NAME,
                **dialect)
            for reference, target in references:
                result = pinyinOperator.isStrictDecomposition(reference)
                self.assertEquals(result, target,
                    "Target %s of %s not reached: %s" \
                        % (repr(target), repr(reference), repr(result)) \
                    + ' (reading %s, dialect %s)' \
                        % (self.READING_NAME, dialect))


class WadeGilesOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'WadeGiles'

    DIALECTS = [{'toneMarkType': 'SuperscriptNumbers'},
        {'toneMarkType': 'None'},
        {'missingToneMark': 'fifth'},
        {'missingToneMark': 'ignore'},
        {'missingToneMark': 'ignore', 'strictSegmentation': True},
        {'strictSegmentation': True},
        {'WadeGilesApostrophe': u"'"},
        {'case': 'lower'},
        ]

    def cleanDecomposition(self, decomposition, reading, **options):
        if not hasattr(self, '_operators'):
            self._operators = []
        for operatorReading, operatorOptions, op in self._operators:
            if reading == operatorReading and options == operatorOptions:
                break
        else:
            op = self.f.createReadingOperator(reading, **options)
            self._operators.append((reading, options, op))

        return op.removeHyphens(decomposition)


# TODO
class WadeGilesOperatorReferenceTest(ReadingOperatorReferenceTest,
    unittest.TestCase):
    READING_NAME = 'WadeGiles'

    DECOMPOSITION_REFERENCES = []

    COMPOSITION_REFERENCES = []

    READING_ENTITY_REFERENCES = []

    GUESS_DIALECT_REFERENCES = [
        (u"K’ung³-tzǔ³", {'toneMarkType': 'SuperscriptNumbers',
            'WadeGilesApostrophe': u'’'}),
        (u"Ssŭma Ch'ien", {'WadeGilesApostrophe': "'"}),
        (u"Shih3-Chi4", {'toneMarkType': 'Numbers'}),
        ]

class GROperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'GR'

    DIALECTS = [{'abbreviations': False},
        {'GRRhotacisedFinalApostrophe': "'"},
        {'GRSyllableSeparatorApostrophe': "'"},
        {'strictSegmentation': True},
        {'case': 'lower'},
        ]

    def cleanDecomposition(self, decomposition, reading, **options):
        if not hasattr(self, '_operators'):
            self._operators = []
        for operatorReading, operatorOptions, op in self._operators:
            if reading == operatorReading and options == operatorOptions:
                break
        else:
            op = self.f.createReadingOperator(reading, **options)
            self._operators.append((reading, options, op))

        return op.removeApostrophes(decomposition)

    def testValidAbbreviatedEntitiesAccepted(self):
        """
        Test if all abbreviated reading entities returned by
        C{getAbbreviatedEntities()} are accepted by C{isAbbreviatedEntity()}.
        """
        if not hasattr(self.readingOperatorClass, "getAbbreviatedEntities"):
            return

        forms = [{}]
        forms.extend(self.DIALECTS)
        for dialect in forms:
            grOperator = self.f.createReadingOperator(self.READING_NAME,
                **dialect)
            entities = grOperator.getAbbreviatedEntities()
            for entity in entities:
                self.assert_(
                    grOperator.isAbbreviatedEntity(entity),
                    "Abbreviated entity %s not accepted" % repr(entity) \
                        + ' (reading %s, dialect %s)' \
                            % (self.READING_NAME, dialect))


#TODO
class GROperatorReferenceTest(ReadingOperatorReferenceTest,
    unittest.TestCase):
    READING_NAME = 'GR'

    DECOMPOSITION_REFERENCES = [
        ({}, [
            (u"tian’anmen", ["tian", u"’", "an", "men"]),
            (u"Beeijing", ["Beei", "jing"]),
            (u"faan-guohlai", ["faan", "-", "guoh", "lai"]),
            (u'"Haeshianq gen Muh.jianq"', ['"', "Hae", "shianq", " ", "gen",
                " ", "Muh", ".jianq", '"']),
            (u"keesh", ["kee", "sh"]),
            (u"yeou ideal", ["yeou", " ", "i", "deal"]),
            (u"TIAN’ANMEN", ["TIAN", u"’", "AN", "MEN"]),
            ]),
        ]

    COMPOSITION_REFERENCES = [
        ({}, [
            (["tian", "an", "men"], u"tian’anmen"),
            (["tian", u"’", "an", "men"], u"tian’anmen"),
            (["Beei", "jing"], u"Beeijing"),
            (["yeou", " ", "i", "deal"], u"yeou ideal"),
            (["faan", "-", "guoh", "lai"], u"faan-guohlai"),
            (["TIAN", "AN", "MEN"], u"TIAN’ANMEN"),
            ]),
        ]

    READING_ENTITY_REFERENCES = [
        ({}, [
            (u"shau", True),
            (u"shao", True),
            (u"shaw", True),
            ]),
        ]

    GUESS_DIALECT_REFERENCES = []

    ABBREVIATED_READING_ENTITY_REFERENCES = [
        ({}, [
            (u"sh", True),
            (u"SH", True),
            ]),
        ]

    def testAbbreviatedEntitiesReferences(self):
        """
        Test if abbreviated reading entity references are accepted by
        C{isAbbreviatedEntity()}.
        """
        for dialect, references in self.ABBREVIATED_READING_ENTITY_REFERENCES:
            grOperator = self.f.createReadingOperator(self.READING_NAME,
                **dialect)
            for reference, target in references:
                result = grOperator.isAbbreviatedEntity(reference)

                self.assertEquals(result, target,
                    "Target %s of %s not reached: %s" \
                        % (repr(target), repr(reference), repr(result)) \
                    + ' (reading %s, dialect %s)' \
                        % (self.READING_NAME, dialect))

    # The following mappings are taken from the Pinyin-to-GR Conversion Tables
    # written/compiled by Richard Warmington,
    # http://home.iprimus.com.au/richwarm/gr/pygrconv.txt
    # and have been extended by rhoticised finals
    SPECIAL_MAPPING = """
zhi             jy      jyr     jyy     jyh
chi             chy     chyr    chyy    chyh
shi             shy     shyr    shyy    shyh
ri              ry      ryr     ryy     ryh
zi              tzy     tzyr    tzyy    tzyh
ci              tsy     tsyr    tsyy    tsyh
si              sy      syr     syy     syh

ju              jiu     jyu     jeu     jiuh
qu              chiu    chyu    cheu    chiuh
xu              shiu    shyu    sheu    shiuh

yi              i       yi      yii     yih
ya              ia      ya      yea     yah
yo              io      -       -       -
ye              ie      ye      yee     yeh
yai             iai     yai     -       -
yao             iau     yau     yeau    yaw
you             iou     you     yeou    yow
yan             ian     yan     yean    yann
yin             in      yn      yiin    yinn
yang            iang    yang    yeang   yanq
ying            ing     yng     yiing   yinq
yong            iong    yong    yeong   yonq

wu              u       wu      wuu     wuh
wa              ua      wa      woa     wah
wo              uo      wo      woo     woh
wai             uai     wai     woai    way
wei             uei     wei     woei    wey
wan             uan     wan     woan    wann
wen             uen     wen     woen    wenn
wang            uang    wang    woang   wanq
weng            ueng    -       woeng   wenq

yu              iu      yu      yeu     yuh
yue             iue     yue     yeue    yueh
yuan            iuan    yuan    yeuan   yuann
yun             iun     yun     yeun    yunn

er              el      erl     eel     ell

yir             iel     yel     yeel    yell
yar             ial     yal     yeal    yall
yer             ie'l    ye'l    yeel    yell
yair            -       yal     -       -
yaor            iaul    yaul    yeaul   yawl
your            ioul    youl    yeoul   yowl
yanr            ial     yal     yeal    yall
yinr            iel     yel     yeel    yell
yangr           iangl   yangl   yeangl  yanql
yingr           iengl   yengl   yeengl  yenql
yongr           iongl   yongl   yeongl  yonql

wur             ul      wul     wuul    wull
war             ual     wal     woal    wall
wor             uol     wol     wool    woll
wair            ual     wal     woal    wall
weir            uel     wel     woel    well
wanr            ual     wal     woal    wall
wenr            uel     wel     woel    well
wangr           uangl   wangl   woangl  wanql
wengr           uengl   -       woengl  wenql

yur             iuel    yuel    yeuel   yuell
yuer            iue'l   yue'l   -       yuell
yuanr           iual    yual    yeual   yuall
yunr            iuel    yuel    yeuel   yuell
"""

    # final mapping without line 'r'
    FINAL_MAPPING = """
a               a       ar      aa      ah              ha      a
o               o       or      oo      oh              ho      o
e               e       er      ee      eh              he      e
ai              ai      air     ae      ay              hai     ai
ei              ei      eir     eei     ey              hei     ei
ao              au      aur     ao      aw              hau     au
ou              ou      our     oou     ow              hou     ou
an              an      arn     aan     ann             han     an
en              en      ern     een     enn             hen     en
ang             ang     arng    aang    anq             hang    ang
eng             eng     erng    eeng    enq             heng    eng
ong             ong     orng    oong    onq             hong    ong

i               i       yi      ii      ih              hi      i
ia              ia      ya      ea      iah             hia     ia
io              io      -       -       -               hio     -
ie              ie      ye      iee     ieh             hie     ie
iai             iai     yai     -       -               hiai    iai
iao             iau     yau     eau     iaw             hiau    iau
iu              iou     you     eou     iow             hiou    iou
ian             ian     yan     ean     iann            hian    ian
in              in      yn      iin     inn             hin     in
iang            iang    yang    eang    ianq            hiang   iang
ing             ing     yng     iing    inq             hing    ing
iong            iong    yong    eong    ionq            hiong   iong

u               u       wu      uu      uh              hu      u
ua              ua      wa      oa      uah             hua     ua
uo              uo      wo      uoo     uoh             huo     uo
uai             uai     wai     oai     uay             huai    uai
ui              uei     wei     oei     uey             huei    uei
uan             uan     wan     oan     uann            huan    uan
un              uen     wen     oen     uenn            huen    uen
uang            uang    wang    oang    uanq            huang   uang

u:              iu      yu      eu      iuh             hiu     iu
u:e             iue     yue     eue     iueh            hiue    iue
u:an            iuan    yuan    euan    iuann           hiuan   iuan
u:n             iun     yun     eun     iunn            hiun    iun

ar              al      arl     aal     all             hal     al
or              ol      orl     ool     oll             hol     ol
er              e'l     er'l    ee'l    ehl             he'l    e'l
air             al      arl     aal     all             hal     al
eir             el      erl     eel     ell             hel     el
aor             aul     aurl    aol     awl             haul    aul
our             oul     ourl    ooul    owl             houl    oul
anr             al      arl     aal     all             hal     al
enr             el      erl     eel     ell             hel     el
angr            angl    arngl   aangl   anql            hangl   angl
engr            engl    erngl   eengl   enql            hengl   engl
ongr            ongl    orngl   oongl   onql            hongl   ongl

ir              iel     yel     ieel    iell            hiel    iel
iar             ial     yal     eal     iall            hial    ial
ier             ie'l    ye'l    ieel    iell            hie'l   ie'l
iair            -       yal     -        -              -       -
iaor            iaul    yaul    eaul    iawl            hiaul   iaul
iur             ioul    youl    eoul    iowl            hioul   ioul
ianr            ial     yal     eal     iall            hial    ial
inr             iel     yel     ieel    iell            hiel    iel
iangr           iangl   yangl   eangl   ianql           hiangl  iangl
ingr            iengl   yengl   ieengl  ienql           hiengl  iengl
iongr           iongl   yongl   eongl   ionql           hiongl   iongl

ur              ul      wul     uul     ull             hul     ul
uar             ual     wal     oal     uall            hual    ual
uor             uol     wol     uool    uoll            huol    uol
uair            ual     wal     oal     uall            hual    ual
uir             uel     wel     oel     uell            huel    uel
uanr            ual     wal     oal     uall            hual    ual
unr             uel     wel     oel     uell            huel    uel
uangr           uangl   wangl   oangl   uanql           huangl  uangl
uengr           uengl   -       -       -               huengl  uengl

u:r             iuel    yuel    euel    iuell           hiuel   iuel
u:er            iue'l   yue'l   euel    iuell           hiue'l  iue'l
u:anr           iual    yual    eual    iuall           hiual   iual
u:nr            iuel    yuel    euel    iuell           hiuel   iuel
"""

    PINYIN_FINAL_MAPPING = {'iu': 'iou', 'ui': 'uei', 'un': 'uen', 'u:': u'ü',
        'u:e': u'üe', 'u:an': u'üan', 'u:n': u'ün', 'iur': 'iour',
        'uir': 'ueir', 'unr': 'uenr', 'u:r': u'ür', 'u:er': u'üer',
        'u:anr': u'üanr', 'u:nr': u'ünr'}

    INITIAL_REGEX = re.compile('^(tz|ts|ch|sh|[bpmfdtnlsjrgkh])?')

    def setUp(self):
        super(GROperatorReferenceTest, self).setUp()

        self.converter = self.f.createReadingConverter('Pinyin',
            'GR', sourceOptions={'Erhua': 'oneSyllable'},
            targetOptions={'GRRhotacisedFinalApostrophe': "'"})
        self.pinyinOperator = self.f.createReadingOperator('Pinyin',
            Erhua='oneSyllable')

        # read in plain text mappings
        self.grJunctionSpecialMapping = {}
        for line in self.SPECIAL_MAPPING.split("\n"):
            if line.strip() == "":
                continue
            matchObj = re.match(r"((?:\w|:)+)\s+((?:\w|')+|-)\s+" \
                + "((?:\w|')+|-)\s+((?:\w|')+|-)\s+((?:\w|')+|-)", line)
            if not matchObj:
                print line
            pinyinSyllable, gr1, gr2, gr3, gr4 = matchObj.groups()

            self.grJunctionSpecialMapping[pinyinSyllable] = {1: gr1, 2: gr2,
                3: gr3, 4: gr4}

        self.grJunctionFinalMapping = {}
        self.grJunctionFinalMNLRMapping = {}
        for line in self.FINAL_MAPPING.split("\n"):
            matchObj = re.match(r"((?:\w|\:)+)\s+((?:\w|')+|-)\s+" \
                + "((?:\w|')+|-)\s+((?:\w|')+|-)\s+((?:\w|')+|-)" \
                + "\s+((?:\w|')+|-)\s+((?:\w|')+|-)", line)
            if not matchObj:
                continue

            pinyinFinal, gr1, gr2, gr3, gr4, gr1_m, gr2_m = matchObj.groups()

            if pinyinFinal in self.PINYIN_FINAL_MAPPING:
                pinyinFinal = self.PINYIN_FINAL_MAPPING[pinyinFinal]

            self.grJunctionFinalMapping[pinyinFinal] = {1: gr1, 2: gr2, 3: gr3,
                4: gr4}
            self.grJunctionFinalMNLRMapping[pinyinFinal] = {1: gr1_m, 2: gr2_m}

    def testGRJunctionGeneralFinalTable(self):
        """
        Test if the conversion matches the general final table given by GR
        Junction.
        """
        # create general final mapping
        entities = self.pinyinOperator.getPlainReadingEntities()
        for pinyinPlainSyllable in entities:
            pinyinInitial, pinyinFinal \
                = self.pinyinOperator.getOnsetRhyme(pinyinPlainSyllable)
            if pinyinInitial not in ['m', 'n', 'l', 'r', 'z', 'c', 's', 'zh',
                'ch', 'sh', ''] and pinyinFinal not in ['m', 'ng', 'mr', 'ngr']:
                for tone in [1, 2, 3, 4]:
                    target = self.grJunctionFinalMapping[pinyinFinal][tone]
                    if target == '-':
                        continue

                    pinyinSyllable = self.pinyinOperator.getTonalEntity(
                        pinyinPlainSyllable, tone)
                    syllable = self.converter.convert(pinyinSyllable)

                    tonalFinal = self.INITIAL_REGEX.sub('', syllable)

                    self.assertEquals(tonalFinal, target,
                        "Wrong conversion to GR %s for Pinyin syllable %s: %s" \
                            % (repr(target), repr(pinyinSyllable),
                                repr(syllable)))

    def testGRJunctionMNLRFinalTable(self):
        """
        Test if the conversion matches the m,n,l,r final table given by GR
        Junction.
        """
        # m, n, l, r mapping for 1st and 2nd tone
        entities = self.pinyinOperator.getPlainReadingEntities()
        for pinyinPlainSyllable in entities:
            pinyinInitial, pinyinFinal \
                = self.pinyinOperator.getOnsetRhyme(pinyinPlainSyllable)
            if pinyinInitial in ['m', 'n', 'l', 'r'] \
                and pinyinFinal[0] != u'ʅ':
                for tone in [1, 2]:
                    target = self.grJunctionFinalMNLRMapping[pinyinFinal][tone]
                    if target == '-':
                        continue

                    pinyinSyllable = self.pinyinOperator.getTonalEntity(
                        pinyinPlainSyllable, tone)
                    syllable = self.converter.convert(pinyinSyllable)

                    tonalFinal = self.INITIAL_REGEX.sub('', syllable)

                    self.assertEquals(tonalFinal, target,
                        "Wrong conversion to GR %s for Pinyin syllable %s: %s" \
                            % (repr(target), repr(pinyinSyllable),
                                repr(syllable)))

    def testGRJunctionSpecialTable(self):
        """
        Test if the conversion matches the special syllable table given by GR
        Junction.
        """
        entities = self.pinyinOperator.getPlainReadingEntities()
        for pinyinPlainSyllable in entities:
            if pinyinPlainSyllable in ['zhi', 'chi', 'shi', 'zi', 'ci',
                'si', 'ju', 'qu', 'xu', 'er'] \
                or (pinyinPlainSyllable[0] in ['y', 'w'] \
                    and pinyinPlainSyllable not in ['yor']): # TODO yor, ri
                for tone in [1, 2, 3, 4]:
                    target = self.grJunctionSpecialMapping[pinyinPlainSyllable]\
                        [tone]
                    if target == '-':
                        continue

                    pinyinSyllable = self.pinyinOperator.getTonalEntity(
                        pinyinPlainSyllable, tone)

                    syllable = self.converter.convert(pinyinSyllable)

                    self.assertEquals(syllable, target,
                        "Wrong conversion to GR %s for Pinyin syllable %s: %s" \
                            % (repr(target), repr(pinyinSyllable),
                                repr(syllable)))


class MandarinBrailleOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'MandarinBraille'

    DIALECTS = [{'toneMarkType': 'None'},
        {'missingToneMark': 'fifth'},
        ]


# TODO
#class MandarinBrailleReferenceTest(ReadingOperatorReferenceTest,
    #unittest.TestCase):
    #READING_NAME = 'MandarinBraille'

    #DECOMPOSITION_REFERENCES = []

    #COMPOSITION_REFERENCES = []

    #READING_ENTITY_REFERENCES = []


class MandarinIPAOperatorConsistencyTestCase(ReadingOperatorConsistencyTest,
    unittest.TestCase):
    READING_NAME = 'MandarinIPA'

    DIALECTS = [{'toneMarkType': 'Numbers'},
        {'toneMarkType': 'ChaoDigits'},
        # {'toneMarkType': 'Diacritics'}, # TODO NotImplementedError
        {'toneMarkType': 'None'},
        {'missingToneMark': 'ignore'},
        ]

    def cleanDecomposition(self, decomposition, reading, **options):
        return [entity for entity in decomposition if entity != '.']


# TODO
#class MandarinIPAReferenceTest(ReadingOperatorReferenceTest,
    #unittest.TestCase):
    #READING_NAME = 'MandarinIPA'

    #DECOMPOSITION_REFERENCES = []

    #COMPOSITION_REFERENCES = []

    #READING_ENTITY_REFERENCES = []